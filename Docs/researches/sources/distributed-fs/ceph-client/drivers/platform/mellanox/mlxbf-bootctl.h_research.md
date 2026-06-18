# sources/distributed-fs/ceph-client/drivers/platform/mellanox/mlxbf-bootctl.h

## Purpose
Header defining the BlueField boot-control Arm SMCCC/SiP ABI consumed by `mlxbf-bootctl.c`. It documents firmware service IDs, reset-action values, fuse query arguments, service version requirements, and large ICM sizing constraints.

## Important APIs, Types, And Constants
Service IDs include watchdog post-reset set/get, reset and second-reset action set/get, TBB fuse status, eMMC reset, DIMM info, firmware reset, manufacturing info set/get/lock, ICM info set/get, OS-up notification, RTC low-battery status, and SiP service discovery/version calls. Reset action constants are `MLXBF_BOOTCTL_EXTERNAL`, `MLXBF_BOOTCTL_EMMC`, `MLNX_BOOTCTL_SWAP_EMMC`, `MLXBF_BOOTCTL_EMMC_LEGACY`, and `MLXBF_BOOTCTL_NONE`. ICM constraints define a 0x80 minimum/granularity and 0x100000 maximum.

## Control Flow
The header has no executable control flow, but its constants drive every SMC dispatch and sysfs validation path in the driver. The driver first checks service identity/version calls and then uses the operational IDs for management operations.

## State, Dependencies, Integration, Risks, Tests
The file represents a firmware contract, not kernel state. Its values must remain synchronized with ATF/firmware implementations; changing IDs or semantic ranges can break boot management. It depends only on preprocessor use by the C driver. Integration points are SMCCC, secure boot lifecycle reporting, reset policy, EEPROM manufacturing storage, and platform provisioning tools. Test signals include compile-time use by `mlxbf-bootctl.c`, service UUID/version compatibility, valid reset-action mappings, and boundary tests for large ICM sizes.
