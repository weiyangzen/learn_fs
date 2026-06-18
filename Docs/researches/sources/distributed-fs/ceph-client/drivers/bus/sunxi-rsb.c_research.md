# sources/distributed-fs/ceph-client/drivers/bus/sunxi-rsb.c

## Purpose
This is the Allwinner Reduced Serial Bus controller and bus core. It registers a custom `sunxi-rsb` bus type, creates child RSB devices from DT, assigns runtime addresses to known hardware addresses, provides read/write transfers, and exposes a regmap bus for RSB client drivers.

## Important APIs, Types, and Functions
`struct sunxi_rsb` holds controller MMIO, clock, reset, completion, mutex, last IRQ status, and target clock frequency. `struct sunxi_rsb_device` and `struct sunxi_rsb_driver` are integrated through the custom bus. Exported APIs are `sunxi_rsb_driver_register()` and `__devm_regmap_init_sunxi_rsb()`. Transfer paths are `sunxi_rsb_read()`, `sunxi_rsb_write()`, and `_sunxi_rsb_run_xfer()`. Probe initializes hardware, sets device mode, registers child devices, and enables runtime PM/autosuspend.

## Control Flow
Module init registers the bus then the platform controller. Probe validates `clock-frequency`, maps registers, gets IRQ/clock/reset, initializes synchronization, requests IRQ, initializes hardware clock/reset and controller timing, sends the device-mode sequence, enables runtime PM, and calls `of_rsb_register_devices()`. Device registration first assigns runtime addresses with the `STRA` command for all known children, then creates `sunxi_rsb_device` instances so client drivers can probe. Transfers are serialized by a mutex, resume the controller via runtime PM, program address/data/command registers, and wait either by IRQ completion or atomic polling when IRQs are disabled.

## State and Persistence
The controller maintains runtime address mappings for children but uses a hardcoded map rather than dynamic allocation. `rsb->status` is set by the IRQ handler. Hardware state includes clock divider, runtime addresses in slaves, device mode, and pending transfer registers. Runtime suspend disables the clock; system suspend asserts reset and reinitializes on resume.

## Dependencies and Integration Points
It depends on CCF clocks, reset control, IRQs, OF child nodes, runtime PM, regmap, and public `linux/sunxi-rsb.h` client abstractions. Clients typically access PMICs or codecs through the exported regmap initializer.

## Risks and Test Signals
Risks include hardcoded runtime address support for only known devices, transfer timeout/abort handling, atomic-poll path differences, lost runtime addresses after full power loss unless resume reinitializes correctly, and custom bus lifetime. Test signals include PMIC regmap reads/writes of 8/16/32-bit widths, timeout/NACK error paths, suspend/resume with child devices, and clean bus unregister on module exit.
