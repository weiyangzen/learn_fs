# sources/distributed-fs/ceph-client/drivers/platform/mellanox/mlxbf-bootctl.c

## Purpose
BlueField boot-control platform driver exposing reset-time controls, secure-boot state, manufacturing EEPROM fields, RSH boot FIFO, RSH logging, large ICM sizing, OS-up notification, firmware reset, and RTC low-battery status through sysfs. It binds to ACPI `MLNXBF04` and validates the Arm SiP service UUID before exposing management state.

## Important APIs, Types, And Functions
Core firmware access goes through `mlxbf_bootctl_smc()` and direct `arm_smccc_smc()` calls using IDs from `mlxbf-bootctl.h`. `boot_names[]` maps reset action strings to firmware values. Sysfs handlers cover `post_reset_wdog`, `reset_action`, `second_reset_action`, `lifecycle_state`, `secure_boot_fuse_state`, `fw_reset`, `rsh_log`, `large_icm`, `os_up`, manufacturing fields (`oob_mac`, `opn`, `sku`, `modl`, `sn`, `uuid`, `rev`), `mfg_lock`, and `rtc_battery`. `mlxbf_bootctl_bootfifo_read()` implements the binary `bootfifo` attribute.

## Control Flow
Probe maps four platform resources: boot FIFO data/count and RSH semaphore/scratch registers. It checks the SiP UUID, resets the default boot action back to eMMC to avoid stale watchdog-triggered swaps, and creates the `bootfifo` binary sysfs file. Sysfs reads issue SMC gets or MMIO reads; writes validate strings, numeric ranges, MAC format, or exact trigger values before calling firmware.

## State, Dependencies, Integration, Risks, Tests
State persists mainly in firmware or EEPROM: reset actions survive resets, manufacturing fields can be locked, large ICM size is stored in EEPROM, and RTC low-battery reads also clear firmware state. Kernel-global MMIO pointers and mutexes serialize ICM, OS-up, MFG, and RTC calls. Dependencies include ACPI resources, Arm SMCCC, sysfs, iopoll, and RSH MMIO layout. Risks are destructive sysfs writes, partial manufacturing writes across multiple SMC objects, RSH log truncation when scratch space is full, endian/packing assumptions for EEPROM strings, and boot-mode side effects at probe. Test signals are ACPI bind success, expected sysfs attributes, SMC error mapping, bootfifo timeout behavior, valid/invalid reset action writes, manufacturing field round trips, and RSH log semaphore timeout handling.
