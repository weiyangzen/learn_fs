# `sources/distributed-fs/ceph-client/include/linux/iio/adc/qcom-adc5-gen3-common.h`

Purpose: shared Qualcomm PMIC ADC5 Gen3 register definitions, channel property structs, thermal-monitor auxiliary wrapper, and common helpers for main and auxiliary ADC/TM drivers.

Important APIs/types/functions: register offsets/status bits, virtual SID/channel packing (`ADC5_GEN3_V_CHAN`), PMIC channel IDs, `enum adc5_cal_method`, `enum adc5_time_select`, `struct adc5_sdam_data`, `struct adc5_device_data`, `struct adc5_channel_common_prop`, `struct tm5_aux_dev_wrapper`, SDAM read/write, handshake polling, digital parameter update, status clear, shared mutex lock/unlock, scaled reading/therm conversion, and TM notifier registration.

Control flow and state: ADC state spans regmap plus one or more SDAM bases/IRQs. Channel properties persist parsed channel configuration: channel, calibration, decimation, SID, label, prescale, settle time, averaging, and scale function. Helpers coordinate register access, conversion request/status clearing, and scaled conversion.

Dependencies/integration: depends on auxiliary bus, bitfield helpers, device/regmap, and `qcom-vadc-common.h`. Integrated with Qualcomm PMIC ADC and thermal monitor drivers.

Risks: wrong SDAM index/base corrupts register access; virtual channel packing must preserve SID/channel fields; handshake/status polling can hang without timeout discipline in implementation; calibration/scale enums must match hardware; shared mutex must protect cross-auxiliary access.

Test signals: SDAM read/write boundaries, conversion request/status clear, multiple SDAMs, SID/channel packing, calibration mode update, thermal code conversion, threshold IRQ/notifier delivery, and probe cleanup of auxiliary devices.
