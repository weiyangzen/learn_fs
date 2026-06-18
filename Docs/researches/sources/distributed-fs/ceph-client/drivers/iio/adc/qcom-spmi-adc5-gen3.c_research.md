# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-adc5-gen3.c

Qualcomm SPMI ADC5 Gen3 driver for PMIC ADC measurements and thermal-monitor sharing. It exposes immediate ADC conversions through IIO, exports helper APIs for an auxiliary ADC thermal-monitor device, and handles SDAM-based handshakes, conversion status clearing, and threshold interrupt dispatch.

`struct adc5_chip` combines IIO state, `struct adc5_device_data` SDAM base/IRQ metadata, channel properties, completion, mutex, ADC data tables, and auxiliary TM linkage. Exported namespace APIs include `adc5_gen3_read/write`, `adc5_gen3_update_dig_param`, `adc5_gen3_poll_wait_hs`, `adc5_gen3_status_clear`, lock helpers, scaled-reading helpers, thermal code conversion, and TM notifier registration. IIO callbacks are `adc5_gen3_read_raw`, `adc5_gen3_read_label`, and `adc5_gen3_fwnode_xlate`.

Probe reads multiple `reg` entries as SDAM bases, collects per-SDAM IRQs, requests the VADC SDAM IRQ, parses child channel nodes, optionally creates an auxiliary `adc5_tm_gen3` device for `qcom,adc-tm` channels, then registers IIO. A read waits for handshake readiness, writes SID/channel/timing/digital/average/settle configuration, requests conversion, waits up to 501 ms, reads little-endian channel data, scales through `qcom_adc5_hw_scale`, and clears EOC status. The ISR completes immediate conversions, clears conversion faults, and forwards TM status to the registered auxiliary handler.

Runtime state includes parsed channel properties, TM channel count, auxiliary device pointer, callback pointer, and SDAM base/IRQ descriptors. Dependencies include parent SPMI regmap, IIO, auxiliary bus, `qcom-adc5-gen3-common.h`, `qcom-vadc-common.c`, and device-tree channel properties.

Risks include the TM callback lifecycle, exported lock ordering with auxiliary code, no polling mode for Gen3 immediate conversions, long PBS handshake/conversion timeouts, and TM channel capacity limits. Test multi-SDAM probe, invalid channel/timing properties, concurrent IIO/TM operations, conversion fault handling, EOC clearing, auxiliary creation, exported helper scaling, and handshake/conversion timeout paths.
