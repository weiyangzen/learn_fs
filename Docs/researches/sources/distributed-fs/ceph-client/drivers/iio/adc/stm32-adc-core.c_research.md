# sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc-core.c

## Purpose
This platform driver is the parent/core for STM32 ADC blocks. It owns shared registers, clocks, regulators, analog switch supplies, common IRQ demultiplexing, runtime PM, and child-device population for individual STM32 ADC IIO instances.

## Important APIs, types, and functions
`struct stm32_adc_priv` contains shared clock/regulator/syscfg resources, IRQ domain, compatible config, common IIO data, and saved common-control register state. `struct stm32_adc_priv_cfg` describes per-family common registers, clock selection, max rate, identification, syscfg capabilities, IRQ count, and ADC count. Important functions include `stm32f4_adc_clk_sel()`, `stm32h7_adc_clk_sel()`, `stm32_adc_irq_handler()`, `stm32_adc_irq_probe()`, `stm32_adc_core_hw_start()`, `stm32_adc_core_hw_stop()`, `stm32_adc_probe_identification()`, and runtime PM callbacks.

## Control flow
Probe maps the common register resource, obtains `vdda`, `vref`, optional `adc` and `bus` clocks, probes optional syscfg/booster/vdd analog-switch support, enables runtime PM, starts shared hardware, validates IP identification when required, reads VREF millivolts, selects a common ADC clock under the compatible-specific maximum, creates an IRQ domain and chained handlers, then populates child ADC nodes. Remove depopulates children, removes IRQ mappings, stops hardware, and disables PM.

## State and persistence
The core persists `common.rate`, `common.vref_mv`, `common.phys_base`, `nb_adc_max`, and `ccr_bak`. Runtime suspend backs up CCR, disables clocks/regulators/switch supplies, and runtime resume restores supplies, clocks, and CCR. Child drivers access `struct stm32_adc_common` through parent driver data.

## Dependencies and integration points
It integrates with regulators `vdda`, `vref`, optional `vdd` and `booster`, optional clocks `adc` and `bus`, syscon phandle `st,syscfg`, irqdomain/chained IRQ, runtime PM, and Open Firmware child population. Compatibles cover STM32F4, STM32H7, STM32MP1, and STM32MP13 ADC cores.

## Risks
Clock selection has strict duty-cycle and rate assumptions; missing mandatory clocks fail differently by family. Analog switch supply selection depends on measured voltages and optional syscfg/booster resources. IRQ demux only forwards EOC when the child has EOC interrupt enabled, so DMA users rely on hardware EOC clearing. Runtime PM failures can cascade to all children.

## Test signals
Test each compatible's clock-selection path, `st,max-clk-rate-hz` clamping, regulator failure unwinds, syscfg/booster/vdd combinations below and above 2.7 V, IPID and child-count validation, chained IRQ forwarding for EOC/OVR, runtime suspend/resume CCR restore, and child population/depopulation.
