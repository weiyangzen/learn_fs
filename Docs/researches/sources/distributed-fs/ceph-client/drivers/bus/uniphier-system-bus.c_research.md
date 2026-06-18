# sources/distributed-fs/ceph-client/drivers/bus/uniphier-system-bus.c

## Purpose
`uniphier-system-bus.c` programs the Socionext UniPhier System Bus Controller chip-select windows from devicetree ranges and then instantiates child devices on the configured external bus.

## Important APIs, Types, And Functions
`struct uniphier_system_bus_priv` stores the MMIO base and eight `uniphier_system_bus_bank` ranges. `uniphier_system_bus_add_bank()` normalizes and validates ranges, `uniphier_system_bus_check_overlap()` rejects overlapping banks, `uniphier_system_bus_check_boot_swap()` swaps CS0/CS1 configuration when hardware boot swap is active, and `uniphier_system_bus_set_reg()` writes SBC base registers.

## Control Flow
Probe maps the controller registers, parses OF ranges, converts each range's high bus address bits to a bank number, rounds physical windows to hardware granularity, rejects duplicates and overlaps, handles boot swap, writes all bank enable/mask registers, saves drvdata, and calls `of_platform_default_populate()`. Resume simply rewrites the saved bank register values.

## State And Persistence
The computed bank table is kept in driver memory and re-applied after system sleep. Hardware-visible state is the SBC_BASE register set. Unused bank 0/1 entries are written as `0xffffffff` rather than disabled because the hardware routes accesses oddly when those entries are zero.

## Dependencies And Integration Points
The file depends on OF range parsing, platform MMIO mapping, and the child devices below the bus node. The devicetree range encoding must carry the bank number in the upper 32 bits of `range.bus_addr`.

## Risks And Edge Cases
Window rounding can expand ranges, so overlap checks after normalization are essential. Addresses above 32 bits are rejected. Boot-swap handling changes bank assignment based on live hardware state, so tests need real boot modes. Resume assumes the saved bank table remains valid and no firmware reconfiguration must be merged.

## Test Signals
Test by booting with populated ranges, empty banks, duplicate banks, overlapping windows, bank numbers over seven, boot-swap on/off, and suspend/resume. Child devices should only probe after the bus windows are programmed.
