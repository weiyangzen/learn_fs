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
