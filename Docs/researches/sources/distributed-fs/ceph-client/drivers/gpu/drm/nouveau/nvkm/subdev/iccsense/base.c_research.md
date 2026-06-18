<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/base.c

## Purpose
Implements Nouveau current/power sensing from BIOS-described INA209/INA219/INA3221 sensors over I2C, including sensor validation, rail creation, sensor configuration, and aggregate power reads.

## Important APIs, Types, And Functions
Important functions include nvkm_iccsense_validate_device, nvkm_iccsense_poll_lane, nvkm_iccsense_ina209/ina219/ina3221_read, nvkm_iccsense_sensor_config, nvkm_iccsense_read_all, nvkm_iccsense_create_sensor/get_sensor, nvkm_iccsense_oneinit, nvkm_iccsense_init, nvkm_iccsense_dtor, nvkm_iccsense_ctor, and nvkm_iccsense_new_.

## Control Flow
oneinit reads BIOS power budget caps, parses ICCSENSE rails, creates validated sensors from external-device BIOS entries and primary/secondary I2C buses, checks supported sensor IDs, records config, creates enabled resistor rails with sensor-specific read callbacks, and stores power limits. init writes config to each sensor. read_all iterates rails and sums calculated power from shunt and bus voltage registers.

## State, Persistence, Dependencies, And Integration
State includes sensor list, rail list, data_valid flag, power_w_max/crit, sensor config/address/type/i2c adapter, and rail resistor/index/read callback. Dependencies are BIOS extdev/iccsense/power_budget parsers, nvkm_i2c_bus_find, I2C register helpers, and supported INA sensor register maps. Integration points are thermal/power management consumers reading total board power.

## Risks And Test Signals
Risks: invalid or unknown sensors disable or taint readings; arithmetic is integer and assumes BIOS resistor milliohms and sensor LSBs; I2C failures abort aggregate reads. Test signals include BIOS parse logs, sensor ID validation, config writes, plausible power readings under load, and graceful behavior when sensors are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/base.c -->
