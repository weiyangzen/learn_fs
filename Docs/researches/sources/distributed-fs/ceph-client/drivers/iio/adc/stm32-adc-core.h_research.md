# sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc-core.h

## Purpose
This header defines the shared register map, bitfields, constants, and common data structure used by the STM32 ADC core parent and STM32 ADC child IIO driver.

## Important APIs, types, and functions
It defines the common block layout: ADC1 at offset 0, ADC2 at `0x100`, ADC3 at `0x200`, and common registers at `0x300`. It provides STM32F4, STM32H7, STM32MP1, and STM32MP13 register offsets and bit masks for status, interrupt enable, control, trigger selection, resolution, DMA mode, calibration, oversampling, common CCR/CSR, option registers, and hardware identification registers. The only type exported is `struct stm32_adc_common`, containing common MMIO base, physical base, analog clock rate, VREF millivolts, and a spinlock for common registers.

## Control flow
The header has no executable flow. Its definitions enable the parent core to configure shared clocks/IRQs/supplies and the child driver to program per-instance conversion, calibration, scan, oversampling, and internal-channel controls using family-specific register specs.

## State and persistence
`struct stm32_adc_common` is the shared runtime state passed from parent to child through platform driver data. Its `rate` and `vref_mv` values are established by the core and consumed by the child for sampling-time and scale calculations. Its spinlock serializes read-modify-write access to common registers such as CCR.

## Dependencies and integration points
The header depends only on kernel bitfield and bit macros. It is included by `stm32-adc-core.c` and `stm32-adc.c`, making it the contract between the parent MFD-like ADC core and individual ADC instance drivers.

## Risks
Because register masks encode multiple SoC generations, a wrong compatible-to-regspec pairing can write valid-looking bits to the wrong offset. Shared constants such as `STM32H7_DMNGT_MASK` intentionally overlap STM32MP13 DMA bits in the child driver, so future edits must preserve that compatibility assumption. `STM32_ADC_MAX_ADCS` constrains IRQ-domain and offset arrays to three instances.

## Test signals
Test coverage is indirect: build all STM32 ADC compatibles, verify register-spec offsets against datasheets, exercise common lock use under multiple child ADCs, and validate scale/sampling computations that consume `struct stm32_adc_common`.
