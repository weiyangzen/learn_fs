# sources/distributed-fs/ceph-client/drivers/misc/tps6594-pfsm.c

## Purpose
`tps6594-pfsm.c` exposes the PMIC Pre-configurable Finite State Machine for TPS6594/TPS6593/LP8764/TPS65224/TPS652G1 devices. It provides a misc character device for register read/write and ioctl commands that trigger standby, low-power standby, firmware update, active, MCU-only, and retention-state transitions.

## Important APIs, Types, and Functions
`struct tps6594_pfsm` stores the miscdevice, parent regmap, and chip ID. File operations are `tps6594_pfsm_read()`, `tps6594_pfsm_write()`, and `tps6594_pfsm_ioctl()`. Retention trigger setup is handled by `tps6594_pfsm_configure_ret_trig()`. IRQ reporting uses `tps6594_pfsm_isr()`. Lifecycle functions are `tps6594_pfsm_probe()` and `tps6594_pfsm_remove()`. UAPI commands come from `<linux/tps6594_pfsm.h>`.

## Control Flow
Probe allocates private data, names a misc device as `pfsm-<chip_id>-0x<reg>`, registers one-shot handlers for each platform IRQ resource, stores drvdata, and registers the misc device. Reads and writes expose PMIC register offsets from 0 to `0x1ff` one byte at a time. Ioctl switches on PMIC commands, updating RTC/FSM trigger registers and chip-specific startup destination fields, with TPS65224/TPS652G1 exclusions for unsupported low-power or MCU-only states. Remove deregisters the miscdevice.

## State and Persistence
The driver stores only miscdevice/regmap/chip ID in software. PMIC FSM trigger, NSLEEP, RTC, startup, and firmware registers persist according to PMIC hardware behavior. The misc file position controls read/write offset within the two-page PMIC window.

## Dependencies and Integration Points
It integrates with the TPS6594 MFD parent, regmap, miscdevice core, platform IRQ resources, and the PFSM ioctl UAPI. Userspace tooling can read/write PMIC page 0 and page 1 registers for firmware-update flows.

## Risks and Edge Cases
Raw register write access through the misc device is powerful and can alter PMIC/NVM state; permissions and userspace tools are critical. `char val` in write may sign-extend before `regmap_write()` depending on architecture/compiler, though only low bits should matter. Unsupported ioctls and unsupported states return `-ENOIOCTLCMD`, which userspace must handle. Register read/write loops are byte-at-a-time and not atomic across multi-byte sequences.

## Test Signals
Validate miscdevice naming, bounded reads/writes and file offsets, each ioctl's register writes for TPS6594-family versus TPS65224/TPS652G1 chips, retention option copying from userspace, IRQ event logging, misc deregistration, and error propagation from `copy_from_user()` and regmap calls.
