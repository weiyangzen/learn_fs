# sources/distributed-fs/ceph-client/drivers/iio/adc/rzn1-adc.c

## Purpose
This platform IIO driver supports the Renesas RZ/N1 ADC controller, which can use ADC1, ADC2, or both internal ADC cores depending on which AVDD and VREF supplies are described. It exposes direct 12-bit raw voltage readings and scale based on each core's VREF.

## Important APIs, types, and functions
`struct rzn1_adc` owns the MMIO base, mutex, device pointer, and per-core VREF millivolt values. Static channel tables represent ADC1-only, ADC2-only, and combined ADC1+ADC2 layouts; scale is shared by type when only one core is present and separate per channel when both cores are present. Core routines are `rzn1_adc_power()`, `rzn1_adc_vc_setup_conversion()`, `rzn1_adc_read_raw_ch()`, `rzn1_adc_get_vref_mV()`, `rzn1_adc_set_iio_dev_channels()`, and `rzn1_adc_core_get_regulators()`.

## Control flow
Probe allocates IIO state, initializes the mutex, maps registers, enables `pclk` and `adc` clocks, probes optional regulator pairs for ADC1 and ADC2, chooses the IIO channel table, enables autosuspended runtime PM, and registers the device. A raw read maps IIO channels 0-7 to ADC1 VC channels and 8-15 to ADC2, resumes runtime PM with cleanup-guard helpers, configures a virtual channel, forces conversion, polls for hardware to clear the force bit, reads the selected data register, and returns the result.

## State and persistence
Persistent state is minimal: VREF values and selected channel table are fixed at probe. Hardware power-down state is controlled through runtime PM by writing `RZN1_ADC_CONFIG_ADC_POWER_DOWN` and polling `ADC_BUSY`. Virtual-channel setup is rewritten for each read.

## Dependencies and integration points
The driver integrates with platform MMIO, clocks named `pclk` and `adc`, optional regulators `adc1-avdd`, `adc1-vref`, `adc2-avdd`, and `adc2-vref`, runtime PM, and the IIO direct-mode API. The compatible is `renesas,rzn1-adc`.

## Risks
`rzn1_adc_read_raw_ch()` assigns `ret = IIO_VAL_INT` but returns `0`, relying on the caller to convert success to `IIO_VAL_INT`; this is harmless but misleading. If only one regulator of a core pair exists, the core is silently treated as unused after enabling the available AVDD, which should be checked against board expectations. Conversion polling uses a 100 us worst-case estimate with atomic polling, so clock assumptions matter.

## Test signals
Test all regulator-presence combinations, no-core probe failure, per-core scale values, channel mapping for ADC1 and ADC2, virtual-channel busy handling, conversion timeout and forced stop path, runtime PM power transitions, and invalid channel guard behavior.
