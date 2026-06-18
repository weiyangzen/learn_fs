# sources/distributed-fs/ceph-client/drivers/scsi/isci/task.h

Purpose: declares the ISCI task-management interface used between libsas callbacks, request construction, and SCI task completion, plus the compact TMF object used by `task.c`.

Important APIs and types: `enum isci_tmf_function_codes` maps ISCI TMF names to libsas TMF opcodes for abort-task and LUN-reset. `struct isci_tmf` carries a completion pointer, SAS protocol, LUN bytes, managed I/O tag, TMF code, completion status, and a response union large enough for SSP response IU or SATA D2H FIS. Public prototypes expose task execution, abort, abort/clear task set, query, LUN reset, nexus reset, completion, and SSP task request accessors.

Control flow role: the header is not executable policy, but it fixes the data contract used when `task.c` builds a TMF, stores a stack completion in `tmf->complete`, and later copies response data in `isci_task_request_complete()`. `isci_print_tmf()` is an inline diagnostic branch that formats either SATA or SSP response fields according to `tmf->proto`.

State and persistence: `struct isci_tmf` is transient per management operation. The response union must remain last because it overlays protocol-specific response layouts and includes the max SSP response buffer. No persistent state exists.

Dependencies and integration: includes libsas ATA helpers and ISCI host definitions. Prototypes bind to libsas domain-template callbacks and SCI request helper functions implemented elsewhere in the ISCI driver.

Risks and test signals: protocol selection must be set before response logging/copying or the wrong union member is interpreted. Future TMF additions need corresponding construct and completion handling. Compile coverage should catch signature drift; runtime debug logs from `isci_print_tmf()` help verify SSP/SATA status propagation.
