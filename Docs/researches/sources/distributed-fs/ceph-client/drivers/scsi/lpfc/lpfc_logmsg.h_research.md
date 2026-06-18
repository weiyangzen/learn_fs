# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_logmsg.h

## Purpose
`lpfc_logmsg.h` defines the LPFC driver's log-category bitmask and the logging macros used by the rest of the driver to route verbose, severity-driven, and trace-triggered messages through the kernel device logger. It is a small but central observability contract: other modules choose masks such as `LOG_MBOX`, `LOG_DISCOVERY`, `LOG_NVME`, or `LOG_TRACE_EVENT`, and these macros decide whether a message is emitted, buffered in the debug trace path, or accompanied by a debug dump.

## Important APIs, Types, and Constants
- `LOG_ELS`, `LOG_DISCOVERY`, `LOG_MBOX`, `LOG_INIT`, `LOG_LINK_EVENT`, `LOG_NODE`, `LOG_SLI`, `LOG_FCP_ERROR`, `LOG_LIBDFC`, `LOG_VPORT`, `LOG_FIP`, `LOG_SCSI_CMD`, `LOG_NVME`, `LOG_NVME_DISC`, `LOG_NVME_ABTS`, `LOG_NVME_IOERR`, `LOG_CGN_MGMT`, `LOG_ENCRYPTION`, and `LOG_TRACE_EVENT` are independent category bits used by `cfg_log_verbose`.
- `LOG_ALL_MSG` is the all-normal-categories mask, deliberately excluding the top trace-event bit.
- `lpfc_dmp_dbg(struct lpfc_hba *phba)` is declared as the debug-log dump hook used when a `LOG_TRACE_EVENT` message is emitted without verbose logging enabled.
- `lpfc_dbg_print(struct lpfc_hba *phba, const char *fmt, ...)` is the fallback buffered/debug trace path for messages not printed to the kernel log.
- `lpfc_vlog_msg()` and `lpfc_log_msg()` are older/simple macros that print when the selected mask is enabled or the severity is warning-or-higher by checking `level[1] <= '5'`.
- `lpfc_printf_vlog()` and `lpfc_printf_log()` are the richer macros used throughout the driver. They print when the mask is enabled or severity is error-or-higher by checking `level[1] <= '3'`; otherwise, when verbose logging is disabled, they call `lpfc_dbg_print()`.

## Control Flow and State
The macros are pure call-site helpers but depend on runtime state from `struct lpfc_hba` and `struct lpfc_vport`. Vport logs use `vport->cfg_log_verbose`; HBA logs prefer `phba->pport->cfg_log_verbose` when a physical port exists and fall back to `phba->cfg_log_verbose` during early initialization. When the category bit is enabled, the macros call `dev_printk()` against `phba->pcidev->dev` and prefix messages with board number and, for vport logging, VPI. If `LOG_TRACE_EVENT` is set and the message is printed because of severity rather than explicit verbosity, the macros first call `lpfc_dmp_dbg()` to dump driver debug state.

## State and Persistence Behavior
No persistent state is stored in this header. Runtime persistence is through the driver's configurable verbose masks and any debug buffers maintained behind `lpfc_dbg_print()`. The macros read flags but do not mutate driver state except for the trace dump side effect.

## Dependencies and Integration Points
The header assumes `struct lpfc_hba`, `struct lpfc_vport`, `pcidev`, `brd_no`, `pport`, `cfg_log_verbose`, and `vpi` are visible from including files. It integrates with Linux `dev_printk()` severity strings such as `KERN_ERR` and with the driver's debug dump/print implementations. The masks are referenced by mailbox setup, discovery state transitions, memory allocation failures, SCSI/NVMe paths, link handling, congestion management, and encryption paths.

## Risks and Edge Cases
- The severity filter indexes `level[1]`, so callers must pass normal `KERN_*` strings; unusual strings would break the severity test.
- Macro arguments reference `phba`, `vport`, and format arguments multiple times conceptually; callers should avoid side-effect expressions.
- `lpfc_printf_log()` dereferences `phba->pcidev`; very early or late teardown call sites must ensure the PCI device pointer remains valid.
- `LOG_TRACE_EVENT` can trigger heavy debug dumping from severe paths, which is useful for failures but risky in log storms.
- Messages below the print threshold may still be captured through `lpfc_dbg_print()` only when verbose logging is disabled; this distinction matters when comparing kernel logs with debug traces.

## Test Signals
Useful signals include boot/probe logs with the expected board and VPI prefixes, dynamic changes to `cfg_log_verbose` enabling category-specific output, severe messages printing even when category masks are disabled, trace-event failures invoking the debug dump hook, and no crashes during early initialization where `phba->pport` is not yet established.
