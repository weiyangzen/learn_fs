<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i3c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i3c.c

Purpose: I3C frontend for ST LSM6DSx devices with known manufacturer/part IDs.

Important APIs/functions: `st_lsm6dsx_i3c_ids` maps I3C IDs to `ST_LSM6DSO_ID` and `ST_LSM6DSR_ID`. `st_lsm6dsx_i3c_probe()` initializes an 8-bit regmap with `devm_regmap_init_i3c()` and calls `st_lsm6dsx_probe(dev, 0, id, regmap)`.

Control flow: I3C core matches IDs, probe creates regmap, and core handles the rest with IRQ set to 0, causing software-triggered buffer setup when hardware FIFO IRQ is unavailable.

State and persistence: no frontend runtime state beyond regmap/core state.

Dependencies and integration: depends on I3C device APIs, regmap I3C, core PM ops, and namespace import `IIO_LSM6DSX`.

Risks: probe assumes `i3c_device_match_id()` returns an ID because the driver was matched. Passing IRQ 0 means no hardware IRQ/FIFO drain path from this frontend. Only two I3C IDs are listed.

Test signals: I3C modalias matching, regmap I3C read/write, software-trigger buffer operation, and PM callback linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i3c.c -->
