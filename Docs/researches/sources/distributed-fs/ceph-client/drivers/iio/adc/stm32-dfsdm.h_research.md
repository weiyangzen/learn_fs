# sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-dfsdm.h

Purpose: shared STM32 DFSDM hardware contract for the core and ADC drivers. It defines channel/filter register offsets, bit masks, field helpers, identification registers, filter-order enums, software resource structures, channel clock-source enum, and the exported DFSDM global start/stop prototypes.

Important APIs/types/functions: macros cover `DFSDM_CHCFGR*`, `DFSDM_AWSCDR`, filter registers `DFSDM_CR1/CR2/ISR/ICR/JCHGR/FCR/*DATAR`, watchdog thresholds/status, and identification registers. `struct stm32_dfsdm_filter_osr`, `struct stm32_dfsdm_filter`, `struct stm32_dfsdm_channel`, and `struct stm32_dfsdm` are the main cross-file types. `enum stm32_dfsdm_sinc_order` and `enum stm32_dfsdm_spi_clk_src` encode filter and serial clock configuration.

Control flow: this header has no runtime execution, but it drives all register programming in the core and ADC files. The core uses identification and global channel fields to size and enable the peripheral; the ADC driver uses channel config, filter config, status, data, DMA, and trigger fields for conversion setup and result handling.

State and persistence: the header models persistent hardware state through register fields and persistent software state through `struct stm32_dfsdm`. Filter OSR entries cache computed IOSR/FOSR, shifts, resolution, and max sample values; channel entries cache serial input type/source/alternate input.

Dependencies and integration: depends on Linux bitfield helpers and is tightly coupled to STM32 DFSDM device-tree bindings and child IIO drivers. The exported prototypes allow child modules to coordinate shared global enable and runtime PM through the parent core.

Risks: register-layout and bitfield correctness is critical; a wrong mask affects every consumer. There are typo-like risks in helper definitions, notably ISR/ICR macros that must match actual use. The structures are shared mutable state without internal locking, so child drivers rely on IIO serialization and parent active-counting.

Test signals: compile-time inclusion by both DFSDM drivers, successful regmap updates for every macro field, correct filter base/address masking for all filter instances, channel count bounds checking, generated OSR programming values, and working exported symbol linkage.
