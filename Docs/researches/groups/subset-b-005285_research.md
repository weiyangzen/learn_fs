# Research Group: subset-b-005285

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_debugfs.c

## Purpose
`lpfc_debugfs.c` implements the LPFC Fibre Channel driver's optional debugfs and instrumented debug dump surface. When `CONFIG_SCSI_LPFC_DEBUG_FS` is enabled and the `lpfc_debugfs_enable` module parameter is set, it builds `/sys/kernel/debug/lpfc/fnX/vportY` and `/sys/kernel/debug/lpfc/fnX/iDiag` entries for tracing discovery, slow-ring, NVMe/NVMET I/O, node state, queue state, mailbox state, congestion buffers, RAS firmware logs, and selected error injection knobs. Outside the debugfs-only build guard it also provides mailbox/queue dump helpers used by instrumented paths.

## Important APIs, Types, And Functions
- Module parameters: `lpfc_debugfs_enable`, `lpfc_debugfs_max_disc_trc`, `lpfc_debugfs_max_slow_ring_trc`, `lpfc_debugfs_max_nvmeio_trc`, and `lpfc_debugfs_mask_disc_trc` control whether debugfs is exposed and how large ring-style traces are.
- Global debug state: `lpfc_debugfs_seq_trc_cnt` gives monotonic trace sequence numbers, `lpfc_debugfs_start_time` anchors trace timestamps, and the static `struct lpfc_idiag idiag` stores the active iDiag command, read offset, and selected queue pointer.
- Trace writers: `lpfc_debugfs_disc_trc()`, `lpfc_debugfs_slow_ring_trc()`, and `lpfc_debugfs_nvme_trc()` append formatted trace entries to per-vport or per-HBA circular buffers.
- Debugfs data builders: `lpfc_debugfs_disc_trc_data()`, `lpfc_debugfs_slow_ring_trc_data()`, `lpfc_debugfs_nodelist_data()`, `lpfc_debugfs_nvmestat_data()`, `lpfc_debugfs_scsistat_data()`, `lpfc_debugfs_ioktime_data()`, `lpfc_debugfs_nvmeio_trc_data()`, `lpfc_debugfs_hdwqstat_data()`, `lpfc_debugfs_hbqinfo_data()`, `lpfc_debugfs_multixripools_data()`, and legacy SLIM dump routines format kernel state into temporary read buffers.
- Debugfs file lifecycle helpers: many `*_open()` routines allocate a `struct lpfc_debug`, populate `debug->buffer`, and rely on `lpfc_debugfs_read()`, `lpfc_debugfs_lseek()`, and `lpfc_debugfs_release()` or specialized `vfree` releases.
- Writable debugfs controls: `*_write()` handlers reset counters, enable/disable timing and hardware queue accounting, resize NVMe I/O trace storage, set DIF error injection state, or parse iDiag commands for PCI config, BAR, queue, doorbell, control register, mailbox, and extent access.
- iDiag helpers: `lpfc_idiag_cmd_get()` parses numeric command lines; `lpfc_idiag_pcicfg_*`, `lpfc_idiag_baracc_*`, `lpfc_idiag_queinfo_read()`, `lpfc_idiag_queacc_*`, `lpfc_idiag_drbacc_*`, `lpfc_idiag_ctlacc_*`, `lpfc_idiag_mbxacc_*`, and `lpfc_idiag_extacc_*` implement the diagnostic command set.
- Registration/teardown: `lpfc_debugfs_initialize()` creates the hierarchy, allocates per-HBA/per-vport trace buffers, normalizes trace sizes down to powers of two, and registers all file operations; `lpfc_debugfs_terminate()` removes directories and frees trace buffers as the last vport/HBA goes away.
- Non-debugfs dump APIs: `lpfc_idiag_mbxacc_dump_bsg_mbox()`, `lpfc_idiag_mbxacc_dump_issue_mbox()`, and `lpfc_debug_dump_all_queues()` print selected mailbox or queue content to the kernel log when diagnostics are active.

## Control Flow
Initialization starts with `lpfc_debugfs_initialize(vport)`. The first HBA creates the `lpfc` root, then a `fn%d` HBA directory, then HBA-level files such as `multixripools`, `cgn_buffer`, `rx_monitor`, `ras_log`, `hbqinfo`, error injection files, slow-ring trace, and NVMe I/O trace. Each vport gets `vport%d` with `discovery_trace`, `nodelist`, `nvmestat`, `scsistat`, `ioktime`, and `hdwqstat`. Physical SLI4 ports additionally get an `iDiag` directory with `pciCfg`, `barAcc`, `queInfo`, `queAcc`, `drbAcc`, `ctlAcc`, `mbxAcc`, and conditionally `extAcc`.

For standard read-only debugfs reports, an `open` handler retrieves `inode->i_private`, allocates `struct lpfc_debug` plus an output buffer, snapshots current driver state into the buffer, and stores it in `file->private_data`. Reads are served by `simple_read_from_buffer()`, seeks use `fixed_size_llseek()` against the captured length, and release frees the buffer. This creates mostly point-in-time snapshots rather than live streaming views.

Trace append paths are hot-path helpers called elsewhere in the driver. They check enable flags/masks, increment atomic counters, choose a ring slot by masking with `size - 1`, and store the format pointer plus three data fields. Dump paths start from the slot after the current producer index and wrap through the ring to preserve chronological order.

iDiag is command-driven. A user first writes an opcode and arguments into a file such as `pciCfg` or `queAcc`; the write handler validates argument count, range, alignment, queue ID, and operation type, and stores command metadata in global `idiag`. A following read consults `idiag.cmd`, performs the selected PCI/MMIO/queue read, formats a page-sized fragment, updates `idiag.offset.last_rd` for browse operations, and returns the text. Some writes execute immediately, such as PCI config writes, BAR writes, queue-entry memory writes, doorbell writes, and control-register writes.

Teardown reverses setup at vport granularity. It frees the vport discovery trace, removes the vport debugfs directory, decrements the HBA vport count, and only when the last vport disappears frees HBA trace buffers, removes the HBA directory, decrements the root HBA count, and removes the root directory when no HBAs remain.

## State And Persistence Behavior
- All state is runtime-only kernel memory; nothing persists across driver unload, reboot, or module reload.
- Trace buffers live in `vport->disc_trc`, `phba->slow_ring_trc`, and `phba->nvmeio_trc`. They are circular, overwrite old entries, and depend on power-of-two sizes.
- Debugfs reads are snapshot-based for most files. The data shown is the state at `open`, not necessarily at subsequent `read`, except for handlers such as `cgn_buffer` and `rx_monitor` that format during read.
- Several file-scope cursors rotate output across reads/opens: `lpfc_debugfs_last_hbq`, `lpfc_debugfs_last_xripool`, optional `lpfc_debugfs_last_lock`, `lpfc_debugfs_last_hba_slim_off`, `phba->lpfc_idiag_last_eq`, and `idiag.offset.last_rd`.
- Counter reset writes mutate live driver counters, including NVMe/NVMET, SCSI, queue accounting, multi-XRI, timing, lock conflict, and DIF injection fields.
- The static global `idiag` is shared across HBAs and debugfs file instances, so concurrent iDiag users can overwrite each other's commands and browse offsets.

## Dependencies And Integration Points
- Depends on Linux debugfs, PCI config access, MMIO `readl/writel`, kernel allocation APIs, atomics, spinlocks, lists, per-CPU helpers, and SCSI/NVMe FC transport structures.
- Integrates tightly with `struct lpfc_hba`, `struct lpfc_vport`, `struct lpfc_nodelist`, SLI3 HBQs/SLIM, SLI4 hardware queues, mailbox paths, RAS firmware logging, congestion management, RX monitor reporting, NVMe initiator and NVMET target statistics, and DIF error injection logic.
- Includes LPFC internal headers for hardware layout (`lpfc_hw*.h`), queue structures (`lpfc_sli*.h`), discovery (`lpfc_disc.h`), NVMe (`lpfc_nvme.h`), BSG mailbox handling (`lpfc_bsg.h`), and debugfs command constants/types (`lpfc_debugfs.h`).
- Debug output is exposed through kernel debugfs permissions, typically root-only in practice, but the files are often created with mode `0644`, relying on debugfs mount permissions and kernel policy for access containment.

## Risks And Edge Cases
- Writable iDiag files can directly modify PCI config space, BAR MMIO registers, queue entries, doorbells, and control registers. This is intentionally diagnostic but can hang or corrupt a live adapter if exposed outside controlled environments.
- The global `idiag` state is not per-file, per-HBA, or locked around multi-step write/read sequences. Concurrent users can race command setup, browse offsets, and mailbox dump criteria.
- Some trace dump routines temporarily set global `lpfc_debugfs_enable = 0` without synchronization, which can drop tracing for all ports while a read is formatting.
- Power-of-two rounding silently lowers requested trace depth; zero depth disables effective trace allocation/open behavior and can return empty output or `-ENOSPC`.
- Several stats and reset writes mutate live counters without broad locking. For diagnostic counters this is acceptable but readers should not assume atomic cross-counter consistency.
- Open handlers allocate fixed-size buffers; output can truncate silently or with explicit "Truncated" markers depending on the path.
- Error injection files directly alter `phba->lpfc_injerr_*` fields. These should be present only in development or controlled testing kernels.
- `debugfs_remove()` removes a single dentry; because only directory dentries are stored, correctness relies on debugfs recursive behavior for directories in the target kernel version.

## Test Signals
- Build with `CONFIG_SCSI_LPFC_DEBUG_FS=y` and without it; without debugfs the trace helper macros/functions should compile to no-op or guarded behavior.
- Mount debugfs and verify hierarchy creation for SLI3 and SLI4 devices, including absence of SLIM files on SLI4 and presence of `iDiag` only on SLI4 physical port setup.
- Exercise read/open/release for each file and verify no leaks on repeated open/close, vport removal, HBA removal, and module unload.
- Validate non-power-of-two module parameters are rounded down and trace dumping preserves chronological ring order.
- Confirm reset writes (`zero`, `reset`, `clear`, `on`, `off`) affect only intended counters and return `-EINVAL` on malformed strings.
- For iDiag, test command validation boundaries: offsets at end of PCI config/BAR ranges, unaligned offsets, invalid queue IDs, invalid register IDs, browse continuation, and concurrent access behavior.
- Use lockdep/KASAN/KCSAN where possible because this file reads and mutates live queue, node, and diagnostic state under mixed locking rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_debugfs.h

## Purpose
`lpfc_debugfs.h` defines the data sizes, command IDs, helper structures, trace masks, and inline queue-dump helpers used by the LPFC debugfs implementation. It also provides a no-op `lpfc_nvmeio_data()` macro when debugfs support is not built, allowing call sites to compile without carrying debugfs conditionals.

## Important APIs, Types, And Constants
- Buffer sizing constants define fixed output capacities for debugfs files, including discovery traces, node lists, SLIM dumps, HBQ/HDWQ reports, NVMe/SCSI stats, congestion info, multi-XRI pools, PCI config/BAR browse buffers, queue access, doorbell/control access, mailbox dumps, extents, and RX monitor reports.
- iDiag command constants encode operation classes: PCI config read/write/set/clear, BAR access, queue access, doorbell register access, control register access, mailbox dump setup, BSG mailbox dump setup, and extent reads.
- Index constants such as `IDIAG_PCICFG_WHERE_INDX`, `IDIAG_QUEACC_QUEID_INDX`, and `IDIAG_MBXACC_DPCNT_INDX` define positional command-line argument layout for `lpfc_idiag_cmd.data[]`.
- `struct lpfc_debug` is the generic per-open debugfs private state, carrying the original object pointer, operation type, output buffer, and length.
- `struct lpfc_debugfs_trc` stores discovery/slow-ring trace entries as a format pointer, three 32-bit data values, sequence count, and jiffies timestamp.
- `struct lpfc_debugfs_nvmeio_trc` stores compact NVMe trace entries with two 16-bit fields and one 32-bit field.
- `struct lpfc_idiag_cmd`, `struct lpfc_idiag_offset`, and `struct lpfc_idiag` define the shared iDiag command, browse offset, active flag, and private object pointer used by `lpfc_debugfs.c`.
- Discovery trace masks such as `LPFC_DISC_TRC_ELS_CMD`, `LPFC_DISC_TRC_MBOX`, `LPFC_DISC_TRC_CT`, `LPFC_DISC_TRC_RPORT`, and `LPFC_DISC_TRC_NODE` let call sites classify entries and let the module mask filter them.
- The dump selector enum (`DUMP_IO`, `DUMP_MBX`, `DUMP_ELS`, `DUMP_NVMELS`) is used by queue dump helpers.
- Declares `void lpfc_debug_dump_all_queues(struct lpfc_hba *);`.

## Inline Debug Dump Helpers
The lower half of the header implements queue dumping helpers used outside the debugfs file-operation path. `lpfc_debug_dump_qe()` validates a queue pointer and index, formats one queue entry in 32-bit words, and emits it through `printk`. `lpfc_debug_dump_q()` emits queue metadata and dumps every entry. Type-specific helpers select IO, mailbox, ELS, NVME LS, EQ, CQ, WQ, RQ, and ID-based queues from `phba->sli4_hba` and call the generic dump routines. These helpers favor direct kernel log diagnostics over debugfs read buffers.

## Control Flow
When `CONFIG_SCSI_LPFC_DEBUG_FS` is enabled, the header exposes concrete structures and constants consumed by `lpfc_debugfs.c` and call sites that append NVMe trace entries. When the config option is disabled, the NVMe trace macro compiles to `no_printk()`, avoiding runtime work while preserving format checking-like call structure. Queue dump helpers are outside the main include guard's debugfs conditional tail and remain available as driver debug utilities.

## State And Persistence Behavior
The header itself owns no storage except inline stack buffers in helper functions. It defines the shape of runtime state held in `struct lpfc_debug`, `struct lpfc_debugfs_trc`, `struct lpfc_debugfs_nvmeio_trc`, and `struct lpfc_idiag`. Those instances are allocated or declared in the implementation and remain transient kernel memory. Format pointers in trace records assume the format strings remain valid for the lifetime of trace entries, which is true for static driver strings but unsafe for dynamic strings.

## Dependencies And Integration Points
- Requires LPFC queue and HBA definitions from surrounding driver headers; many helpers dereference `struct lpfc_hba`, `struct lpfc_queue`, and `phba->sli4_hba`.
- Uses kernel logging (`printk`, `pr_err`, `dev_printk`), fixed line sizes such as `LPFC_LBUF_SZ`, and queue accessor `lpfc_sli4_qe()`.
- The iDiag constants must stay in sync with command parsing and validation in `lpfc_debugfs.c`.
- Trace masks are used by discovery and ELS/CT/RSCN paths elsewhere in the LPFC driver when calling `lpfc_debugfs_disc_trc()`.

## Risks And Edge Cases
- Fixed buffer sizes are part of the ABI-like debugfs behavior; increasing output without increasing the corresponding size can truncate reports.
- Command constants and argument indexes are numeric and positional, so mismatches between documentation, user scripts, and parser code can lead to wrong hardware access.
- Inline dump helpers print entire queues to the kernel log and can produce large logs on adapters with many or deep queues.
- The no-op `lpfc_nvmeio_data()` macro under non-debugfs builds suppresses side effects in arguments only if callers do not rely on those side effects; call sites should pass pure diagnostic expressions.
- Helper routines assume SLI4 queue pointers exist for the selected queue type. They do basic null checks in some places but not all nested dereferences are fully defensive.

## Test Signals
- Compile both debugfs-enabled and debugfs-disabled configurations to verify conditional macros and declarations line up.
- Run sparse or compiler warnings around inline helpers to catch missing prototypes, format mismatches, and pointer type assumptions.
- Exercise `lpfc_debug_dump_all_queues()` and ID-based dump helpers on an SLI4 HBA with mailbox, ELS, NVME LS, IO, CQ, EQ, header RQ, and data RQ queues populated.
- Confirm every iDiag command constant and index used here is accepted or rejected as intended by the implementation's write handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_disc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_disc.h

## Purpose
`lpfc_disc.h` defines LPFC discovery-layer data structures, node state constants, node flags, worker event types, and Fibre Channel/NVMe role metadata. It is the shared contract for representing remote NPorts, discovery state-machine inputs, delayed recovery work, target/initiator roles, registration state with SCSI/NVMe transports, and outstanding RRQ/XRI tracking.

## Important APIs, Types, And Constants
- Discovery limits: `FC_MAX_HOLD_RSCN`, `FC_MAX_NS_RSP`, `FC_MAXLOOP`, and `LPFC_DISC_FLOGI_TMO` bound RSCN deferral, NameServer response size, loop device count, and FLOGI timeout behavior.
- `enum lpfc_work_type` lists asynchronous work events such as online/offline transitions, warm start, kill, ELS retry, devloss, fast-path management events, HBA reset, and port recovery.
- `struct lpfc_work_evt` is the generic queued work item with list linkage, two opaque arguments, and event type.
- `struct lpfc_fast_path_event` wraps `lpfc_work_evt`, a vport pointer, and a union of SCSI/fabric/read-check event payloads for events raised from fast path code.
- `struct lpfc_node_rrqs` and `struct lpfc_node_rrq` support RRQ/XRI tracking. The bitmap form tracks active XRIs per node for SLI4; the list form records xritag, rxid, DID, vport, and stop time for individual RRQ handling.
- `struct lpfc_enc_info` records encryption status and CNSA level for a node session.
- `enum lpfc_fc4_xpt_flags` tracks whether the node is registered with LPFC, SCSI, and NVMe transport layers and whether NVMe unregister is waiting.
- `enum lpfc_nlp_save_flags` names conditions that keep a node alive across devloss/recovery, pending LOGO, or pending DA_ID.
- `struct lpfc_nodelist` is the central node object: list membership, service parameters, WWPN/WWNN, per-node spinlock, FC ID, last ELS command, role/type flags, FC4 capabilities, RPI/XRI/SID, retry and class info, NVMe NSLER/first-burst fields, encryption info, timers, owning HBA/vport, SCSI and NVMe transport rports, work events, kref, command depth, active RRQ bitmap, PRLI tracking, save flags, and NPIV wait queues.
- Node role/type masks include `NLP_FC_NODE`, `NLP_FABRIC`, `NLP_FCP_TARGET`, `NLP_FCP_INITIATOR`, `NLP_NVME_TARGET`, `NLP_NVME_INITIATOR`, and `NLP_NVME_DISCOVERY`.
- FC4 type masks include `NLP_FC4_NONE`, `NLP_FC4_FCP`, and `NLP_FC4_NVME`.
- `enum lpfc_nlp_flag` defines bit numbers for protocol and lifecycle flags such as sent PLOGI/PRLI/ADISC/LOGO, received PLOGI, unregister in progress, dropped initial ref, delay timer active, devloss in progress, deferred removal, target authentication required, FirstBurst support, and valid RPI.
- Node states `NLP_STE_*` define the discovery state machine from unused through PLOGI/ADISC/REG_LOGIN/PRLI/LOGO issue, unmapped, mapped, NPR, and freed.
- Node events `NLP_EVT_*` enumerate received ELS requests, ELS completions, REG_LOGIN completion, device removal, and device recovery.
- `lpfc_ndlp_check_qdepth(phba, ndlp)` checks node command depth against SLI4 maximum configured XRI.

## Control Flow And State Model
The comments describe the discovery state machine. Nodes can reside on PLOGI, ADISC, unmapped, mapped, and binding-related lists. Link up and RSCN processing move nodes from mapped/unmapped lists into ADISC or PLOGI processing lists, issue batches of ELS commands, and feed completions/events through the state machine. Successful Fibre Channel login moves nodes to the unmapped list; PRLI and binding assignment can move FCP targets to mapped. Link down sends recovery/removal events to nodes on active lists; devloss expiry ultimately removes nodes.

`struct lpfc_nodelist` is both a protocol state object and an integration object. It stores current and previous node state, transport registration flags, outstanding command accounting, timers, deferred work items, saved keepalive conditions, and references to transport remote-port objects. Fast-path and recovery code can queue `lpfc_work_evt` entries using the event enum, while discovery code uses `NLP_EVT_*` inputs to transition `nlp_state`.

## State And Persistence Behavior
All state is in-memory driver state associated with an HBA/vport and remote port discovery lifetime. `kref` controls object lifetime, `nlp_delayfunc` supports delayed ELS actions, and `save_flags` protects nodes from premature free under recovery-sensitive operations. `cmd_pending` and `cmd_qdepth` provide live I/O pressure state. The active RRQ bitmap and RRQ list fields track outstanding exchanges that require cleanup. No persistent storage is defined by this header.

## Dependencies And Integration Points
- Depends on kernel list, spinlock, timer, waitqueue, kref, atomic, bitmap, and bit definitions.
- Integrates with Fibre Channel service parameters (`struct serv_parm`), LPFC WWN types (`struct lpfc_name`), HBA/vport structures, SCSI transport `struct fc_rport`, and LPFC NVMe transport `struct lpfc_nvme_rport`.
- Used by debug and observability code such as `lpfc_debugfs_nodelist_data()` to render node state, role flags, transport flags, encryption state, command depth, and deferred DID.
- Defines events and states consumed by discovery, ELS, RSCN, devloss, NPIV, SCSI, and NVMe integration code across the LPFC driver.

## Risks And Edge Cases
- `nlp_flag` is an `unsigned long` bitset using enum bit positions; flag updates must use atomic bit operations or hold the proper node lock where required.
- Node lifetime is subtle because timers, queued work, SCSI rports, NVMe rports, devloss, LOGO, DA_ID, and discovery lists can all retain or refer to the same object.
- The discovery state machine comments are the primary local description of legal transitions; inconsistent transitions can leave nodes on wrong lists or registered with a transport after removal.
- `lpfc_ndlp_check_qdepth()` assumes SLI4 `max_cfg_param.max_xri` is valid for the HBA; callers in non-SLI4 paths need care.
- `LPFC_SLI4_MAX_XRI` fixes the node bitmap to 1024 XRIs, so adapters or firmware configurations exceeding that assumption would require structural changes.
- The union in `lpfc_fast_path_event` relies on forward-declared event payloads being complete before actual allocation/use in translation units that include this header.

## Test Signals
- Discovery tests should cover link up, RSCN, link down, devloss expiry, PLOGI/ADISC/PRLI/LOGO completions, and device recovery/removal events.
- Transport integration tests should verify SCSI/NVMe rport registration and unregister flags are consistent with `nlp_state`, `nlp_type`, and `fc4_xpt_flags`.
- Lifetime tests should stress delayed ELS timers, queued `els_retry_evt`, `dev_loss_evt`, `recovery_evt`, NPIV wait queues, and kref release ordering.
- Debugfs nodelist output is a useful manual signal because it exposes state names, DID/WWNs, RPI, type flags, encryption status, reference count, outstanding I/O, transport flags, and deferred DID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_disc.h -->
