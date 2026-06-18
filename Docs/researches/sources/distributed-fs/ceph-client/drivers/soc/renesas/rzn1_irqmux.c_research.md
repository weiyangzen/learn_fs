# sources/distributed-fs/ceph-client/drivers/soc/renesas/rzn1_irqmux.c

## Purpose

`rzn1_irqmux.c` programs the Renesas RZ/N1 GPIO interrupt multiplexer. It reads the DT `interrupt-map`, validates parent GIC SPI lines, and writes child interrupt sources into eight mux output registers.

## Important APIs, Types, and Functions

`rzn1_irqmux_parent_args_to_line_index()` validates a parent interrupt specifier and converts GIC SPI numbers 103 through 110 into output indexes 0 through 7. `rzn1_irqmux_probe()` maps registers, validates `#interrupt-cells = <1>` and `#address-cells = <0>`, iterates `of_imap_item`s, rejects duplicate outputs, and writes child hwirq values to `regs[index]`.

## Control Flow

Probe maps MMIO, validates binding shape, initializes the OF interrupt-map parser, then for each map item determines the output line and programs the mux. The driver does not register an IRQ domain; it configures static routing described by DT.

## State and Persistence Behavior

No driver-private state persists after probe except devm mapping. The programmed mux registers persist in hardware until reset or later writes.

## Dependencies and Integration Points

It depends on platform MMIO, OF interrupt-map parsing, ARM GIC binding constants, and RZ/N1 GPIO interrupt routing. It is selected by `ARCH_RZN1` when DW APB GPIO is enabled.

## Risks and Edge Cases

The code assumes register spacing matches `u32 __iomem *regs` indexing. It validates duplicate parent outputs but not whether child hwirq values are in a hardware-supported source range. Error paths manually drop `parent_args.np` for early returns inside the iterator.

## Test Signals

Use DT overlays with valid maps, duplicate outputs, invalid GIC type, out-of-range SPI numbers, wrong interrupt/address cell counts, and malformed maps. Verify programmed register values on hardware.
