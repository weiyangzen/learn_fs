# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-rradc.c

Qualcomm Round Robin ADC driver for PM660/PMI8998 PMICs. It exposes battery ID/thermistor, skin/die/charger temperatures, USB/DC voltage/current, and GPIO voltage channels as IIO channels, using mostly continuously updated PMIC ADC registers plus per-channel trigger handling where required.

`struct rradc_channel` describes label, data/status registers, size, optional trigger register/mask, and post-process function. `struct rradc_chip` stores regmap/base, PMIC revision data, conversion mutex, battery ID settle/current metadata, and device pointer. Core helpers include `rradc_read` with coherent double-read retry, `rradc_read_status_in_cont_mode`, `rradc_prepare_batt_id_conversion`, `rradc_do_conversion`, `rradc_read_scale`, `rradc_read_offset`, `rradc_read_raw`, and `rradc_get_fab_coeff`.

Probe gets parent regmap, base, optional battery-ID settle delay, PMIC subtype/fab information, selects an IIO name, and registers a fixed channel array. Reads dispatch by mask: scale and offset are computed from constants and PMIC fab coefficients; raw and processed reads call `rradc_do_conversion`. Conversion takes `conversion_lock`, enables special battery-ID conversion or trigger/continuous mode, checks readiness, coherent-reads channel data, selects the valid battery-ID range when needed, and returns raw code or post-processed resistance.

State includes PMIC revision pointer, optional programmed battery ID delay, and last battery-ID current range. Hardware continuous/log/trigger bits are toggled around reads and restored. Dependencies include SPMI parent regmap, `qcom_pmic_get`, IIO direct mode, fixed PMIC register layout, Linux units helpers, and little-endian conversions.

Risks include coherent retry exhaustion returning a successful regmap code, `-ENODATA` for unattached channels, required fabric coefficients for charger temperature, empirical battery-ID settling/range selection, and GPIO processed reads lacking a `scale_fn`. Test coefficient selection, batt-id delay DT values, coherent-read retries, no-cable paths, trigger cleanup, scale/offset reads, and concurrent channel reads.
