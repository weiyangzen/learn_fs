<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ixp4xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ixp4xx.c

## Purpose
`gpio-ixp4xx.c` implements the Intel IXP4xx SoC GPIO controller, including GPIO access, interrupt-parent translation, and optional clock-output muxing on GPIO14/15.

## Important APIs, types, and functions
`struct ixp4xx_gpio` embeds `gpio_generic_chip`, device/base pointers, and `irq_edge` state. IRQ functions are ack, mask, unmask, set_type, and `ixp4xx_gpio_child_to_parent_hwirq()`. Probe configures clock output bits, initializes gpio-generic, and sets hierarchical IRQ metadata.

## Control flow
Probe maps the MMIO resource, finds the parent IRQ domain, handles DT properties for GPIO14/15 clock outputs and board-specific forced GPIO mode, initializes a generic chip with endian flags based on CPU endianness, registers 16 GPIOs with fixed base 0, and wires a hierarchical irqchip. Type setup writes three-bit trigger style fields in GPIT1/GPIT2, acknowledges status, forces IRQ lines to input, and asks the parent for level-high handling.

## State and persistence behavior
Hardware stores output, direction, input, status, trigger style, debounce select, and clock mux state. `irq_edge` tracks which child IRQs are edge-triggered so unmask can avoid inappropriate level acknowledgements.

## Dependencies and integration points
The driver binds to `intel,ixp4xx-gpio`, depends on DT interrupt parents, gpio-generic, hierarchical irqdomains, and board compatibility strings for special clock mux behavior.

## Risks and edge cases
Only GPIO lines 0-12 map to dedicated parent IRQs; GPIO13-15 cannot become child IRQs. The fixed gpiochip base is a legacy ABI constraint. Endianness must match CPU mode because raw accessors and gpio-generic byte-order flags interact.

## Test signals
Test get/set/direction on big- and little-endian builds, IRQ mapping for lines 0-12 and rejection for 13-15, all trigger styles, GPIO14/15 clock-output DT properties, and board quirks forcing clock mux off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ixp4xx.c -->
