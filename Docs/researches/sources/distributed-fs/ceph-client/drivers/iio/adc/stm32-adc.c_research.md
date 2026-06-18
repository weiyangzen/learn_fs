# sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc.c

## Purpose
This is the STM32 ADC child IIO driver for individual ADC instances below the STM32 ADC core. It supports direct conversions, hardware-triggered buffered capture, optional DMA, differential inputs, internal channels, sampling-time setup, oversampling, debugfs register access, calibration, and runtime/system PM across STM32F4, STM32H7, STM32MP1, and STM32MP13 families.

## Important APIs, types, and functions
`struct stm32_adc` is the main state object: common parent data, instance offset, config, completion, PIO buffer, clock, IRQ, spinlock, conversion counts, resolution, trigger polarity, DMA resources, channel preselection/differential masks, sampling register images, calibration data, internal-channel map, and oversampling index. `struct stm32_adc_cfg` and `struct stm32_adc_regspec` provide family-specific operations and register layout. Key functions include `stm32_adc_single_conv()`, `stm32_adc_read_raw()`, `stm32_adc_write_raw()`, `stm32_adc_conf_scan_seq()`, `stm32_adc_set_trig()`, ISR/threaded ISR pair, DMA buffer callbacks, firmware channel parsers, `stm32h7_adc_prepare()`, self-calibration helpers, and PM callbacks.

## Control flow
Probe obtains parent common data, reads the instance `reg` offset, maps the per-instance IRQ supplied by the parent IRQ domain, obtains the optional per-instance clock, selects resolution, optionally requests DMA, parses either generic child channel nodes or legacy `st,adc-channels` properties, sets up triggered buffers, enables runtime PM, starts hardware, registers IIO, and creates calibration debugfs files. Direct raw reads claim direct mode, resume the parent device, program sampling registers and a one-channel sequence, disable external trigger detection, enable EOC IRQ, start conversion, wait for completion, stop conversion, disable IRQ, autosuspend, and return the sample. Buffered mode updates scan sequence, configures trigger mux, starts DMA or PIO IRQ collection, and pushes samples through IIO buffers.

## State and persistence
Resolution, oversampling index, trigger polarity, sampling-time register images, internal-channel enables, calibration factors, PCSEL/DIFSEL masks, and DMA buffers persist for the life of the device. Runtime suspend stops hardware and may power down/calibrate again on resume depending on family. H7-like variants save or restore linear calibration factors to avoid repeating full linear calibration after the first successful run.

## Dependencies and integration points
The driver depends on the STM32 ADC core's `struct stm32_adc_common`, IIO core, IIO triggers, STM32 timer/LPTIM trigger helpers, DMAengine, runtime PM, debugfs, nvmem cell `vrefint`, firmware channel descriptions, and family compatibles. It uses parent VREF for scale and parent physical base for DMA source address.

## Risks
This is a high-state driver with many SoC-specific register layouts. Risks include stale or missing `vrefint` calibration causing internal VREF channel omission, DMA residue/accounting errors in cyclic buffers, overrun recovery requiring buffer restart, trigger-name matching only for STM32 timer/LPTIM triggers, complex calibration restore paths, and raw processed VREF math dividing by the just-read sample without checking zero. Firmware parser behavior differs between legacy and generic bindings, so channel ordering and sampling times need careful compatibility testing.

## Test signals
Test each compatible's probe, direct raw reads, processed VREFINT with valid/missing/zero nvmem, differential scale/offset, oversampling available/write paths, trigger polarity and timer-trigger validation, PIO buffered mode with timestamps, DMA cyclic mode and watermarks, overrun threaded recovery, runtime and system suspend/resume with active buffers, legacy and generic firmware channel parsing, debugfs register access, and calibration save/restore on H7/MP1.
