# sources/distributed-fs/ceph-client/drivers/iio/adc/ingenic-adc.c

## Purpose
`ingenic-adc.c` is an IIO ADC driver for Ingenic JZ47xx SoCs. It supports auxiliary and battery direct reads across several SoC variants and, on JZ4770-style parts, touchscreen scan channels through a software buffer.

## Important APIs, types, and functions
- `struct ingenic_adc_soc_data` captures variant-specific reference voltages, availability tables, channel tables, feature flags, and clock-divider initialization.
- `struct ingenic_adc` stores MMIO base, prepared clock, register lock, auxiliary lock, SoC data, and battery low-vref mode.
- `ingenic_adc_set_adcmd()` builds touchscreen conversion command sequences based on active scan mask.
- `ingenic_adc_capture()` enables an ADC engine, polls until hardware clears it, and temporarily disables command-select to avoid wrong VBAT reads.
- `ingenic_adc_read_raw()` and `ingenic_adc_write_raw()` expose raw/scale reads and battery reference-mode writes.
- `ingenic_adc_buffer_enable()` and `ingenic_adc_buffer_disable()` configure touchscreen scanning and clock lifetime.
- `ingenic_adc_irq()` reads touch data registers and pushes buffered samples.

## Control flow
Probe selects SoC data from OF, requests the IRQ, maps MMIO, gets a prepared ADC clock, enables it long enough to program clock dividers and passive hardware state, applies optional internal VBAT divider selection, disables the clock, sets IIO direct plus software-buffer modes, and registers the device. Direct reads enable the clock, serialize auxiliary channel selection, trigger the chosen engine, read result registers, and disable the clock. Buffer enable keeps the clock on and programs touchscreen command scanning until buffer disable.

## State and persistence
Driver state includes `low_vref_mode` and SoC data. Hardware state includes ADC engine enables, config bits for auxiliary selection, battery reference mode, command sequence, wait/same registers, interrupt mask/status, and clock dividers. User writes can change battery scale mode on supported SoCs; it is not persisted across reset.

## Dependencies and integration points
The driver uses platform/OF compatibles for JZ4725B/JZ4740/JZ4760/JZ4760B/JZ4770, MMIO, IRQs, common clocks, IIO direct and software buffer modes, fwnode xlate by channel ID, and SoC-specific ADC DT binding constants.

## Risks
- Direct auxiliary reads and buffered touchscreen scans share command/config registers; `lock` and `aux_lock` protect key paths but changes must preserve ordering.
- Clock divider calculations depend on parent clock rates falling within hardware ranges.
- Touch IRQ buffering pushes three 32-bit words based on scan mask pairs; consumer expectations must match scan layout.
- JZ4740 high battery reference uses a floating expression cast into integer constants, so exact scale ABI should be treated carefully.

## Test signals
Test each SoC data table, clock divider edge rates, direct aux/battery reads, battery scale availability and writes, fwnode xlate, buffer enable/disable register cleanup, touch IRQ samples for different scan masks, and internal-divider property handling.
