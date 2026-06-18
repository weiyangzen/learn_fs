# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress-regs.h

## Purpose

This register header maps the IPU7/IPU8 buttress, power bridge, firmware boot parameter, security, IPC, power, clock, CSI PHY, and interrupt register space.

## Important APIs, Types, and Functions

It defines register offsets for IRQ status/enable/clear/mask, TSC/PB timestamps, workpoint and power status, sleep/clock overrides, firmware control/security/source registers, access blockers, boot parameter entries, memory ECC status, IPC registers, PB error logs, and CSI PHY offsets. It also defines interrupt bits, power state masks, IPC command/response constants, frequency ratios, security masks, D2D/NDE fields, UCX control bits, and PB config offsets.

## Control Flow

No code flow exists. `ipu7-buttress.c`, `ipu7-boot.c`, and `ipu7-isys-csi-phy.c` use these offsets and masks to program hardware state machines.

## State and Persistence Behavior

The file describes MMIO state owned by hardware. Some values, such as idle watchdog, boot params, and IRQ masks, are cached/restored by the driver.

## Dependencies and Integration Points

It is the central register contract for buttress power/auth/IPC, firmware boot, and CSI PHY configuration.

## Risks and Edge Cases

Incorrect offsets or masks can corrupt hardware control state. Some registers are generation-specific (`IPU7_` vs `IPU8_`, PTL/PB timestamp paths). A typo-like macro `BUTTRESS_REG_PS_AB_REGION_MAX_ADDRESS0` references `i` in its replacement and should be handled cautiously by consumers.

## Test Signals

Hardware smoke tests for IRQ clear/enable, runtime power up/down, CSE IPC, firmware boot params, TSC sync, and CSI PHY bring-up validate this header.
