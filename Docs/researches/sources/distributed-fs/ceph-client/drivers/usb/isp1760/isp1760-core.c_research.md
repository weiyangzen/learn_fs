# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-core.c

## Purpose
`isp1760-core.c` is the common device layer for NXP ISP1760/1761/1763 controllers. It maps MMIO, creates regmaps and regmap fields for host and device register layouts, performs chip reset and board-mode setup, selects memory layout, and registers the HCD and/or UDC role.

## Important APIs, Types, And Functions
Public functions are `isp1760_register()`, `isp1760_unregister()`, and `isp1760_set_pullup()`. Internal setup is in `isp1760_init_core()`. The file defines memory layouts for ISP1760/1761 and ISP1763, host and device `regmap_config` structures, volatile register ranges, and large `reg_field` arrays keyed by enums from `isp1760-regs.h`.

## Control Flow
`isp1760_register()` first checks that at least one compiled/enabled role can be registered. It allocates `struct isp1760_device`, records devflags, validates bus width constraints, chooses ISP1763 versus ISP1760/1761 register tables, gets an optional reset GPIO, maps the memory resource, initializes host and device regmaps on the same base, allocates all host and device regmap fields, selects the memory layout, and calls `isp1760_init_core()`.

`isp1760_init_core()` toggles reset GPIO if present, performs all-device reset, applies bus width, overcurrent, DACK/DREQ polarity, interrupt polarity, and edge/level flags, configures common IRQ and initial device-controller interrupt state for ISP1761, and programs OTG control for host or peripheral mode. After core init, `isp1760_register()` conditionally calls `isp1760_hcd_register()` and `isp1760_udc_register()`, unwinding HCD if UDC registration fails. Unregister removes UDC then HCD.

## State And Persistence
State is held in devm-managed `struct isp1760_device`, `struct isp1760_hcd`, `struct isp1760_udc`, regmaps, regmap fields, optional reset GPIO, and hardware registers. No durable persistence exists; hardware mode is reprogrammed on probe/reset. `dev_set_drvdata()` ties the state to the platform/PCI device for removal.

## Dependencies And Integration Points
The file depends on regmap MMIO, GPIO descriptors, USB role configuration, IRQ flags, memory resources, and the local HCD/UDC/register headers. It integrates with platform and PCI glue through `isp1760_register()` and with gadget pullup control through `isp1760_set_pullup()`.

## Risks
Regmap-field arrays must stay exactly aligned with enum values; missing or wrong `REG_FIELD()` entries can redirect register writes. ISP1763 has 16-bit register access and different field widths; regressions often appear only on that variant. Device and host regmaps share the same MMIO base with different register maps, so volatile ranges and max registers must remain correct. UDC enablement is inferred from ISP1761/ISP1763 flags, not only peripheral mode, so role logic must be changed carefully.

## Test Signals
Test probe on ISP1760, ISP1761, and ISP1763 descriptions; validate scratch/chip ID reads in role code; verify bus-width flags, reset GPIO timing, interrupt polarity flags, and peripheral-host OTG control writes. Build/test host-only, gadget-only, and dual-role configurations. Failure-injection should cover regmap field allocation, HCD registration failure, and UDC registration failure unwind.
