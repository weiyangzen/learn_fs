# sources/distributed-fs/ceph-client/drivers/mfd/fsl-imx25-tsadc.c

## Purpose
`fsl-imx25-tsadc.c` is the MFD parent for the Freescale i.MX25 touchscreen/ADC block. It maps the shared register block, configures ADC clocking and power mode, creates a two-entry child IRQ domain, and populates touchscreen/ADC child devices.

## Important APIs, Types, and Functions
`mx25_tsadc_regmap_config` describes the 32-bit MMIO register map. `mx25_tsadc_irq_handler()` demultiplexes GCQ and TCQ interrupt status bits to domain hwirqs 1 and 0. `mx25_tsadc_domain_map()` installs `dummy_irq_chip` with `handle_level_irq`. `mx25_tsadc_setup_irq()` and `mx25_tsadc_unset_irq()` manage the chained parent IRQ and domain. `mx25_tsadc_setup_clk()` computes and writes the ADC divider.

## Control Flow
Probe allocates `struct mx25_tsadc`, maps MMIO, initializes regmap, gets the `ipg` clock, programs an ADC divider that keeps conversion clock under 1.75 MHz, enables the block clock/reset/reference voltage/power-saving mode, creates the child IRQ domain, stores driver data, and populates OF children. Remove unsets the chained IRQ and removes the domain.

## State and Persistence
State is per-device regmap, clock, and IRQ domain. Hardware register state includes clock divider, block enable/reset, power mode, internal reference, and interrupt status. No suspend cache exists.

## Dependencies and Integration Points
It depends on platform MMIO/IRQ resources, regmap-mmio, clock framework, irqdomain, chained IRQ helpers, and OF child population. Child touchscreen and ADC drivers consume the shared regmap and two child IRQ lines through the MFD parent data.

## Risks and Edge Cases
The code reads the clock rate before explicitly enabling the clock; it assumes rate querying works while disabled. Divider calculation floors through hardware-specific behavior below four. The chained handler does not ACK status bits itself, relying on child handling or hardware behavior. `irq_domain_create_simple()` with fixed two entries assumes exactly TCQ and GCQ children.

## Test Signals
Check ADC divider values across IPG rates, register writes for reset/power/reference, child IRQ mapping for hwirqs 0 and 1, chained dispatch for TCQ/GCQ status bits, OF child population, and cleanup on child population failure.
