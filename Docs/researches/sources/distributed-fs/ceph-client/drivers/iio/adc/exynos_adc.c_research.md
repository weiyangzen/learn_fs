# sources/distributed-fs/ceph-client/drivers/iio/adc/exynos_adc.c

## Purpose
`exynos_adc.c` supports Samsung S3C, S5PV210, Exynos v1, Exynos v2, Exynos3250, Exynos4212/4412, and Exynos7 ADC blocks as direct-mode IIO voltage devices. It abstracts register-layout differences behind per-compatible callbacks for hardware init, shutdown, IRQ clearing, and conversion start.

## Important APIs, types, and functions
- `struct exynos_adc` stores variant data, MMIO base, optional PMU syscon regmap, clocks, IRQ, regulator, completion, result value, and a mutex.
- `struct exynos_adc_data` describes channel count, bit mask, clock/PHY needs, PMU offset, and operation callbacks.
- `exynos_adc_v1_init_hw()`, `exynos_adc_v2_init_hw()`, and `exynos_adc_exynos7_init_hw()` program prescalers, resolution, reset, interrupt enable, and optional ADC PHY power.
- `exynos_read_raw()` reports regulator-derived scale or starts a conversion and waits on `completion`.
- `exynos_adc_isr()` reads the result, clears the variant IRQ, and completes the conversion.
- Probe/remove and suspend/resume manage regulators, clocks, IRQ, IIO registration, and child device population.

## Control flow
Probe matches the DT compatible to an `exynos_adc_data`, maps registers, optionally finds `samsung,syscon-phandle`, gets `adc` and optional `sclk`, enables the `vdd` regulator, prepares/enables clocks, requests the IRQ, registers the IIO device, initializes hardware, and populates child nodes under the IIO device. A raw read serializes access with `lock`, reinitializes the completion, calls the variant `start_conv()`, waits up to 100 ms, and resets hardware on timeout.

## State and persistence
State is volatile: current conversion value, completion state, enabled clocks/regulator, PMU ADC PHY power, and configured ADC registers. There is no file-backed persistence. Suspend disables hardware and regulator power; resume re-enables and reinitializes the ADC.

## Dependencies and integration points
The driver uses platform devices, OF matching, IIO direct mode, Linux completions, IRQ handling, common clocks, regulator consumers, syscon/regmap for PMU PHY control, and `of_platform_populate()` for ADC child nodes such as touchscreen consumers.

## Risks
- `exynos_adc_get_data()` assumes an OF match exists; invalid binding paths can break probe.
- V1 and V2 register offsets overlap through macros, so callback/data mismatches would read or write the wrong registers.
- Resume returns immediately if clock enable fails after regulator enable, potentially leaving regulator enabled on the error path.
- Conversion timeout resets hardware while the mutex is held, which is correct but should be validated under IRQ loss.

## Test signals
Compile all Exynos/S3C variants, boot-test representative v1 and v2 SoCs, validate scale from `vdd`, read each exposed channel count per compatible, exercise suspend/resume, and test timeout behavior by masking IRQs or using fault injection.
