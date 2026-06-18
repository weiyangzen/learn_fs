# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_errors_abi.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_errors_abi.h

### Purpose
`guc_errors_abi.h` names GuC response, load, and bootrom status codes so driver diagnostics can interpret firmware boot and command failures.

### Important APIs, Types, And Functions
It defines `enum intel_guc_response_status`, `enum intel_guc_load_status`, and `enum intel_bootrom_load_status`, including ready, exception, invalid init-data, KLV workaround errors, and bootrom cryptographic/load-location failures.

### Control Flow
The header has no executable logic; values are consumed by status dump and load-failure handling code.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
No state is stored. It integrates with GuC load-status registers and log/debug output. Risks are stale status names or overlapping ranges that mislead diagnostics. Test signals are meaningful `GUC_STATUS` decoding after boot, load failure, and firmware exception paths.
