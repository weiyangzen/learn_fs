# sources/distributed-fs/ceph-client/drivers/usb/storage/initializers.c

## Purpose

`initializers.c` contains special one-off initialization hooks for unusual USB Mass Storage devices that need vendor commands before normal transport use.

## Important APIs, Types, and Functions

`usb_stor_euscsi_init()` sends a vendor control request to put Shuttle/SCM USB-SCSI bridge devices into multi-target mode. `usb_stor_ucr61s2b_init()` sends a custom bulk CBW-like packet containing a PCChips activation string and reads a CSW to activate all slots on the UCR-61S2B flash reader. `usb_stor_huawei_e220_init()` sends a standard device `SET_FEATURE` request to switch Huawei E220 devices into multi-port mode.

## Control Flow

These functions are called through unusual-device table init hooks during usb-storage setup. Each sends its device-specific command sequence and logs the result. The eUSCSI and Huawei helpers return success regardless of control request status, while the UCR helper returns `-EIO` on failed bulk command or status transfer.

## State and Persistence Behavior

No host-side state is stored. The functions change device firmware mode for the current attachment, such as multi-target, multi-slot, or multi-port behavior. That state normally lasts until reset or unplug.

## Dependencies and Integration Points

The file depends on usb-storage control and bulk transfer helpers, bulk-only wrapper structs, unusual-device init-function wiring, and `debug.h` logging. It integrates before normal SCSI scanning so the device presents the intended targets or interfaces.

## Risks and Test Signals

Risks include ignored failures in two initializers, hard-coded magic request values and strings, fixed timeouts, and reuse of `us->iobuf` for CBW/CSW overlays. Test signals include devices switching to the expected mode before scan, UCR slot visibility, Huawei interface mode change, eUSCSI target discovery, and failure injection for control/bulk transfers.
