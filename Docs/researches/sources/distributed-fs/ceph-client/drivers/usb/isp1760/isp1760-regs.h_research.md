# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-regs.h

## Purpose
`isp1760-regs.h` is the register map and field enum contract for ISP1760/1761/1763 host and peripheral controllers. It centralizes MMIO offsets, bit masks, endpoint interrupt macros, endpoint type constants, and enum indexes used by regmap-field arrays.

## Important APIs, Types, And Functions
The host section defines ISP1760/1761 EHCI capability/operational offsets, PTD done/skip/last maps, hardware mode, chip ID, scratch, reset, buffer status, memory, interrupt masks, and OTG control registers. `enum isp176x_host_controller_fields` assigns stable indexes for host regmap fields.

The device section defines endpoint interrupt macros (`DC_IEPTX`, `DC_IEPRX`, `DC_IEPRXTX`), interrupt/status bit masks, OTG bit masks, endpoint type values, ISP176x DC register offsets, `enum isp176x_device_controller_fields`, and ISP1763 DC register offsets.

## Control Flow
There is no executable control flow. Core code maps enum values to `REG_FIELD()` definitions; HCD and UDC code use enum values through regmap-field helpers and raw offsets for data/FIFO and interrupt access.

## State And Persistence
The file describes hardware register state but stores none itself. The enum order is persistent ABI within this driver: every array indexed by these enums must match exactly.

## Dependencies And Integration Points
The header integrates core, HCD, and UDC. It depends on the kernel `BIT()` macro from including contexts. Device-tree bindings and datasheets must remain aligned with compatible-specific offset sets and chip IDs.

## Risks
Enum ordering is a high-risk maintenance point. Adding a field in the middle without updating all ISP1760 and ISP1763 `reg_field` arrays corrupts field access. Some names are shared between set/clear alias registers and normal registers, so variant-specific code must choose correct offsets. Host and device register spaces differ significantly between ISP1760/61 and ISP1763.

## Test Signals
Compile tests catch only missing enum entries if arrays use sentinel indexes; runtime scratch, chip ID, port control, endpoint FIFO, and interrupt tests are needed for real offset validation. Variant-specific tests should cover both 32-bit ISP1760/61 and 16-bit ISP1763 paths.
