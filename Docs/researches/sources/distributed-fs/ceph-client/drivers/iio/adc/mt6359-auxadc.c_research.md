# sources/distributed-fs/ceph-client/drivers/iio/adc/mt6359-auxadc.c

Purpose: this driver exposes MediaTek PMIC AUXADC channels for several PMIC families, including MT6357, MT6358, MT6359, MT6363, and MT6373. It handles normal AUXADC voltage/current/temperature/resistance reads, battery impedance special cases, SPMI register-width differences, PMIC-specific channel tables, and optional external VIN channel selection.

Important APIs, types, and functions: `struct mt6359_auxadc` stores the regmap, chip descriptor, lock, and timeout recovery flag. `struct mtk_pmic_auxadc_chan` describes request/readiness registers, external selector state, averaging samples, and resistor ratios. `struct mtk_pmic_auxadc_info` selects channel arrays, register maps, reference voltage, PMIC bus mode, reset policy, and impedance callback. `mt6359_auxadc_sample_adc_val()` starts a request, waits for averaging, polls ready bits, and reconstructs 16-bit SPMI values when needed. `mt6359_auxadc_read_adc()` manages external selectors and unconditional stop. `mt6358_read_imp()` and `mt6359_read_imp()` implement impedance flows. `mt6359_auxadc_read_raw()` dispatches scale, normal reads, and impedance reads.

Control flow: probe picks match data, chooses the correct regmap parent for SPMI versus PMIC-wrapper devices, resets supported ADC blocks, then registers the chip-specific IIO channel table. Reads are serialized with `adc_dev->lock`; scale is computed from descriptor resistor ratios and chip VREF, while raw paths request conversion, wait/poll, stop conversion, mask to channel realbits, and update the timeout flag.

State and persistence: all mutable state is in the per-device structure and PMIC registers. `timed_out` persists across reads so a second timeout can trigger a reset on reset-capable PMICs. Energy or samples are not buffered in software.

Dependencies and integration points: it integrates with MT6397-style MFDs, SPMI MFD parents, Linux regmap, DT compatibles, MediaTek AUXADC dt-bindings, and IIO direct mode. External VIN channels depend on PMIC SDMADC selector bits and pullup settings.

Risks: register tables and channel descriptors must match each PMIC exactly; a wrong request or ready bit can hang reads. Stop failures can leave ADC sampling active and are only surfaced via later timeout recovery. SPMI high/low byte handling is easy to break. Impedance read paths use undocumented/partly unknown bits, so regressions need hardware validation. `no_reset` PMICs cannot recover from stuck ADCs through this driver.

Test signals: test every compatible's channel count, labels, scale math, normal raw conversions, SPMI byte reconstruction, external VIN selector cleanup, impedance VBAT/IBAT paths, repeated timeout reset behavior, and `-EOPNOTSUPP` on unsupported impedance channels.
