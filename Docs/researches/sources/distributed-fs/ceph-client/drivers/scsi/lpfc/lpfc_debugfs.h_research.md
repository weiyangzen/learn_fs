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
