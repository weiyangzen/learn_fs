<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.c

Purpose: This file reports zPCI recovery/status events into the s390 debug feature using a custom prolog that includes operation, status, PCI channel state, FID, and FH.

Important APIs/types/functions: The exported function is `zpci_report_status(struct zpci_dev *zdev, const char *operation, const char *status)`. Local structures are `struct zpci_report_error_data` and `struct zpci_report_error`; helpers include `zpci_state_str`, `debug_log_header_fn`, `debug_prolog_header`, and `debug_log_view`.

Control flow: A caller supplies zdev plus operation/status strings. The function builds a small packed record containing channel state and function identifiers, then logs it through `debug_event` with a view whose prolog prints a human-readable header.

State and persistence: Report data is persisted only in the in-memory s390 debug log buffer. It snapshots zPCI function handle/id and PCI channel state at report time.

Dependencies and integration points: It depends on s390 `debug.h`, zPCI debug feature registration, PCI channel state enums, and event/recovery code in `pci_event.c`.

Risks and test signals: Operation/status strings are stored as pointers in the debug event data path, so callers should pass static or otherwise long-lived strings. State-string mapping must cover relevant PCI channel states. Tests include recovery success/failure events, debugfs/debug feature output formatting, and NULL or removed-device avoidance by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.c -->
