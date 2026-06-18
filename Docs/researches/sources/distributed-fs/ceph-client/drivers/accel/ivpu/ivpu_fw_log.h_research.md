## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw_log.h

### Purpose
`ivpu_fw_log.h` defines firmware log levels, firmware log buffer sizes, and firmware log helper prototypes.

### Important APIs, Types, And Functions
It exports log-level constants from default through fatal, verbose buffer sizes of 1 MiB and 8 MiB, critical buffer size of 512 KiB, `ivpu_fw_log_level`, and prototypes for print/mark-read/reset functions.

### Control Flow
There is no executable flow except consumers passing `only_new_msgs` to the print API to choose full versus incremental reads.

### State, Persistence, And Dependencies
The header stores no state beyond the extern module parameter declaration. Buffer size macros affect persistent BO allocation in firmware init.

### Integration Points
It is included by firmware allocation, debugfs, coredump, and fallback diagnostics.

### Risks
Changing buffer sizes changes firmware boot-parameter expectations and memory footprint. Log-level constants must match firmware API values.

### Test Signals
Verify BO sizes allocated for critical/verbose logs, module parameter parsing, boot params carrying log addresses/sizes, and debugfs/coredump compilation with this header.
