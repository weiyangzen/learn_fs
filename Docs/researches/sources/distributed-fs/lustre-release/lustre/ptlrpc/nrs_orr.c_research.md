# sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_orr.c

## Purpose

`nrs_orr.c` implements two related server-side NRS policies for OST I/O: ORR, object-based round robin over backend filesystem objects, and TRR, target-based round robin over OST indices. Both batch requests by object or target, sort within a batch by logical or physical offset, and expose runtime controls for quantum, offset mode, and supported RPC types.

## Important APIs, Types, and Functions

Shared state is `struct nrs_orr_data` for a policy instance and `struct nrs_orr_object` for an object or target bucket. Request-specific state lives in `nr_u.orr` fields such as key, range, round, sequence, and cached physical/key flags. Main hooks are `nrs_orr_init`, `nrs_orr_start`, `nrs_orr_stop`, `nrs_orr_ctl`, `nrs_orr_res_get`, `nrs_trr_res_get`, `nrs_orr_res_put`, `nrs_orr_req_get`, `nrs_orr_req_add`, `nrs_orr_req_del`, `nrs_orr_req_stop`, and `nrs_trr_req_stop`. `orr_req_compare` is the heap comparator. Exported configurations are `nrs_conf_orr` and `nrs_conf_trr`, both compatible only with `ost_io`.

Important helpers include `nrs_orr_req_supported`, `nrs_orr_key_fill`, `nrs_orr_range_fill_logical`, `nrs_orr_range_fill_physical`, `nrs_orr_range_fill`, ORR rhashtable operations, TRR XArray lookup/insert, and debugfs conversion helpers for supported request types.

## Control Flow

Start allocates `nrs_orr_data`, creates an atomic-grow heap, creates a per-instance slab cache, and initializes either an ORR rhashtable or a TRR XArray. Defaults are quantum 256, supported requests set to `NOS_DFLT`, physical offset ordering enabled, and sequence seeded to 1. `nrs_orr_init` logs when the policy is used on a service with multiple CPTs, because per-partition scheduling may reduce policy effectiveness.

Resource acquisition first returns the top-level scheduler resource. The second level rejects unsupported opcodes so requests fall back to FIFO or another policy. ORR fills a key from the OST object FID derived from the request OST body and server OST index; TRR uses the server OST index directly. Both fill an offset range from `RMF_OBD_IOOBJ` and `RMF_NIOBUF_REMOTE`; if physical mode is enabled for reads and the call may sleep, ORR/TRR attempts FIEMAP through `obd_get_info` and falls back to logical offsets on failure. ORR stores bucket objects in an RCU-protected rhashtable with refcounts and frees them after removal via `call_rcu`. TRR stores stable target buckets in an XArray and frees them at stop.

Enqueue applies the same batched round-robin algorithm used by CRR-N, but the bucket is an object FID for ORR or OST index for TRR. The request is tagged with bucket round and sequence, inserted into the heap, and the bucket's active count and remaining quantum are updated. The comparator sorts by round, then bucket sequence, then range start, then shorter range end. Dispatch and dequeue remove heap nodes, update active counts, and advance the global round to the next heap root.

Debugfs control is shared between ORR and TRR through `nrs_lprocfs_orr_data`. Each policy exports quantum, offset type (`physical` or `logical`), and supported request type (`reads`, `writes`, or `reads_and_writes`) files. Read and write paths apply settings separately to regular and HP NRS heads and treat stopped instances as skippable `-ENODEV` cases.

## State and Persistence Behavior

All scheduler state is volatile per service partition and NRS queue. `od_quantum`, `od_supp`, and `od_physical` are runtime debugfs settings. ORR bucket objects are reference-counted and can be removed when their resource references drop to zero; TRR bucket objects are retained in the XArray for the policy lifetime. Request keys and physical-offset flags are cached in `nr_u.orr` so HP movement does not need to repeat sleeping or already completed work.

## Dependencies and Integration Points

The file depends on NRS core hooks, OST request layouts (`RMF_OST_BODY`, `RMF_OBD_IOOBJ`, `RMF_NIOBUF_REMOTE`), `ostid_to_fid`, server data OST indices, FIEMAP via `obd_get_info(KEY_FIEMAP)`, Lustre binheap utilities, rhashtable, XArray, RCU, slab caches, PTLRPC debugfs/lprocfs helpers, and regular/HP queue policy control. It integrates only with the `ost_io` PTLRPC service and only schedules `OST_READ` and `OST_WRITE` when enabled.

## Risks and Edge Cases

Unsupported request types, missing exports, missing request capsule fields, or key/range fill errors cause the policy to reject the request and rely on fallback scheduling. Physical offset lookup can sleep, so HP movement and atomic contexts use cached or logical offsets. FIEMAP failure silently falls back to logical ordering, which is safer but may surprise performance investigations. ORR has complex rhashtable insertion races and refcount-zero retry behavior; resize pressure can loop with short delays. Runtime settings are noted as accessed unlocked in scheduling paths. Multiple CPTs reduce global ordering because each partition schedules independently.

There are parser risks in debugfs paths: bare offset and supported-string writes rely on the buffer start when no named regular/HP value is found, so invalid or empty strings must be rejected cleanly. TRR does not define an `op_res_put` hook because its XArray buckets are retained until stop, unlike ORR's refcounted bucket removal.

## Test Signals

Tests should cover ORR object key generation from OST body and server index, TRR target key generation, unsupported opcode fallback, missing export/capsule failures, logical range extraction, physical FIEMAP success and fallback, HP move using cached request data, heap ordering by round, sequence, start offset, and shorter end offset, quantum exhaustion and inactive-bucket behavior, ORR rhashtable race/refcount cleanup, TRR XArray duplicate insertion, stop cleanup with RCU barrier, and all debugfs controls for regular/HP/bare values. Performance tests should compare single-CPT and multi-CPT behavior, and read/write support toggles should be verified against `OST_READ` and `OST_WRITE` traffic.
