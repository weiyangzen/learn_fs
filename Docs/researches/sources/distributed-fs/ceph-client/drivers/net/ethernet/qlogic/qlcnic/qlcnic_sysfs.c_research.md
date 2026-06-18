# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sysfs.c

### Purpose
`qlcnic_sysfs.c` exposes qlcnic diagnostic and management controls through sysfs and optional hwmon. It supports bridged mode, diagnostic mode, LED beaconing, CRB/memory access, NPAR/eswitch/port-mirroring configuration, port/eswitch statistics, PCI function reporting, 83xx flash access, and ASIC temperature reporting.

### Important APIs, Types, And Functions
Public functions include `qlcnic_create_sysfs_entries()`, `qlcnic_remove_sysfs_entries()`, `qlcnic_82xx_add_sysfs()`, `qlcnic_82xx_remove_sysfs()`, `qlcnic_83xx_add_sysfs()`, `qlcnic_83xx_remove_sysfs()`, `qlcnic_register_hwmon_dev()`, and `qlcnic_unregister_hwmon_dev()`. Key handlers cover `bridged_mode`, `diag_mode`, `beacon`, binary `crb`, `mem`, `npar_config`, `pci_config`, `port_stats`, `esw_stats`, `esw_config`, `pm_config`, and 83xx `flash`.

### Control Flow
Attribute creation is capability/opmode dependent. Basic bridged-mode sysfs is created when firmware advertises bridge support. Diagnostic entries always expose port stats, skip privileged controls for non-privileged functions, skip most controls in maintenance mode, and add eswitch/NPAR/PM/stat entries only when supported and running as management function. Read/write handlers validate sizes, offsets, function IDs, VLAN/bandwidth values, opmodes, and diagnostic-mode state before calling firmware helpers. Flash writes use command tokens to set erase/bulk/write mode and then perform locked flash operations.

### State, Persistence, And Dependencies
State changes include adapter flags (`QLCNIC_DIAG_ENABLED`, bridge, LED), NPAR cached fields, eswitch settings, VLAN/PVID state, flash contents, and hwmon device registration. Dependencies are Linux sysfs/bin_attribute APIs, RTNL for netdev feature changes, qlcnic firmware mailbox helpers, 82xx/83xx register accessors, flash locks, and optional `CONFIG_QLCNIC_HWMON`.

### Integration Points
These sysfs files are used by diagnostics and management tools outside normal netdev/ethtool paths. Beacon operations integrate with diagnostic resource allocation when the device is down. Hwmon exposes temperature under the standard sensor interface while skipping VF devices.

### Risks
CRB/memory and flash interfaces are powerful and gated mainly by diagnostic mode, opmode, offset/size checks, and flash locks. The static `flash_mode` in the write handler is shared across devices and calls, which is a notable state-coupling risk. Binary structures are endian-swapped in-place, so callers must match kernel structure layouts. Partial sysfs creation failures only log warnings, so remove paths must tolerate missing files.

### Test Signals
Test sysfs creation/removal for 82xx, 83xx, management, non-privileged, VF, maintenance, and eswitch modes. Validate invalid CRB/mem offsets, beacon while resetting/down/up, NPAR bandwidth bounds, eswitch VLAN/default validation, PM same-port validation, flash read/write/erase error paths, stats clear/read behavior, and hwmon registration/unregistration.
