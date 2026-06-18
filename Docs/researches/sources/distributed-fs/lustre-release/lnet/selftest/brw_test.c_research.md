# sources/distributed-fs/lustre-release/lnet/selftest/brw_test.c

## Purpose
`brw_test.c` implements the LNet selftest bulk read/write test service and client operations. It allocates bulk buffers, fills them with deterministic magic patterns, sends or receives SRPC bulk transfers, validates returned data, supports older and newer bulk-length session formats, and optionally injects data corruption for negative testing.

## Important APIs, Types, And Functions
- Module parameters `brw_srv_workitems` and `brw_inject_errors` control server workitem capacity and random-ish corruption injection.
- Constants `BRW_POISON`, `BRW_MAGIC`, and `BRW_MSIZE` define data patterns and alignment.
- Client lifecycle: `brw_client_init`, `brw_client_fini`, `brw_client_prep_rpc`, and `brw_client_done_rpc`.
- Pattern helpers: `brw_inject_one_error`, `brw_fill_page`, `brw_check_page`, `brw_fill_bulk`, and `brw_check_bulk`.
- Server callbacks: `brw_server_handle`, `brw_bulk_ready`, `brw_server_rpc_done`, `brw_srpc_init`, and `brw_srpc_fini`.
- Exported registration objects: `struct sfw_test_client_ops brw_test_client`, `struct srpc_service brw_test_service`, and `brw_init_test_service`.

## Control Flow
Client initialization reads the test parameters from the session. For sessions without `LST_FEAT_BULK_LEN`, it uses the legacy page-count request and assumes offset zero. For newer sessions, it uses explicit byte length and offset. It rejects unaligned offsets, lengths greater than `LNET_MTU`, invalid read/write opcodes, and invalid check modes. Then it allocates one `srpc_bulk` buffer per test unit on the destination CPT and stores it in `tsu_private`.

For each client RPC, `brw_client_prep_rpc` creates an SRPC test RPC sized to the request's page count and length, copies the preallocated bulk descriptor into the RPC, fills WRITE bulks with `BRW_MAGIC` and READ bulks with `BRW_POISON`, and sets BRW request flags/opcode/length. Completion checks RPC transport status, handles byte-swapped replies, records BRW status failures in `sn_brw_errors`, and validates READ data against `BRW_MAGIC`.

The server allocates a maximum-MTU bulk buffer per server RPC during `brw_srpc_init`. `brw_server_handle` validates request magic/endian, opcode, check flags, session features, legacy alignment, and length. It initializes the server bulk as sink for writes or source for reads, fills READ data with `BRW_MAGIC`, and poisons WRITE receive buffers before bulk transfer. `brw_bulk_ready` validates WRITE data after transfer and sets `EBADMSG` in the reply on corruption. `brw_server_rpc_done` logs final bulk transfer status.

`brw_init_test_service` caps server workitems by available memory. It starts from one-sixteenth of total RAM, divides by the number of pages needed for an MTU-sized bulk, and lowers `sv_wi_total` if the module parameter would consume too much memory.

## State And Persistence Behavior
Runtime state is per selftest session, test instance, test unit, and SRPC. Client bulk buffers live in `tsu_private` and are freed in `brw_client_fini`. Server bulk buffers live in `srpc_server_rpc.srpc_bulk` and are freed by the service finalizer. Error counts are accumulated in the session's `sn_brw_errors`. The file persists no data to disk.

`brw_inject_errors` is mutable module parameter state. `brw_inject_one_error` decrements it when injection fires based on current nanosecond parity, so error injection is nondeterministic and global to the module.

## Dependencies And Integration Points
The file depends on `selftest.h`, the selftest framework (`sfw_test_instance`, `sfw_test_unit`, `sfw_session`), SRPC bulk and service APIs, LNet MTU and CPT helpers, kernel page memory, byte-swap helpers, and atomic session counters. The registration objects are consumed by the selftest framework and module initialization code linked by the Makefile.

## Risks
- The legacy feature path assumes `blk_npg * PAGE_SIZE` and explicitly notes it does not work for variable page size compatibility.
- Bulk offset and length must be aligned to `BRW_MSIZE` for pattern checking. Incorrect request construction is rejected, but future callers could bypass assumptions.
- `unsafe_memcpy` copies a flexible `srpc_bulk` descriptor into RPC storage using calculated `npg`; mismatches between allocation and `npg` would be memory-corruption prone.
- Fault injection is time-parity based, so repeated tests can be flaky unless the module parameter is controlled and expectations tolerate nondeterminism.
- Server reply status uses positive errno values in the protocol and client converts them to negative `crpc_status`; callers need to preserve that convention.
- Memory consumption is bounded in `brw_init_test_service`, but per-RPC maximum-MTU allocation can still be significant on large concurrency tests.

## Test Signals
Signals include successful READ and WRITE BRW selftests with `CHECK_NONE`, `CHECK_SIMPLE`, and `CHECK_FULL`; legacy and `LST_FEAT_BULK_LEN` sessions; endian-swapped request/reply handling; invalid opcode/flags/length rejection; injected corruption producing `EBADMSG` and incremented `sn_brw_errors`; and workitem cap behavior under constrained memory.
