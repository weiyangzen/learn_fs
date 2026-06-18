<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx.h -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx.h

Purpose: central type, constant, channel, and helper contract for the ST LSM6DSx core, FIFO buffer, sensor-hub, and bus modules.

Important APIs/types: defines device-name constants and `enum st_lsm6dsx_hw_id`; channel macros; register descriptor structs; ODR, full-scale, FIFO, timestamp, shub, event, and whole-device settings structs; sensor IDs; `struct st_lsm6dsx_sensor`; `struct st_lsm6dsx_hw`; exported PM ops and core/helper prototypes; locked regmap helper inlines; mount-matrix ext info; and `st_lsm6dsx_device_set_enable()` dispatching internal sensors vs external shub sensors.

Control flow: bus probes call `st_lsm6dsx_probe()`. Core allocates `st_lsm6dsx_hw` and per-sensor `iio_dev`/`st_lsm6dsx_sensor` objects based on settings tables. Buffer and shub code operate on shared masks, locks, and settings through this header.

State and persistence: `st_lsm6dsx_hw` persists device-wide regmap, IRQ, locks, suspend/enable/FIFO masks, timestamp gain, pattern sizes, event state, IIO device array, orientation, and aligned scan buffers. Each sensor stores ODR, FIFO ODR, gain, watermark, decimator, samples-in-pattern, timestamp reference, and external sensor metadata.

Dependencies and integration: depends on IIO, regulator, device property/platform data conventions, regmap through forward declarations, and common ST sensor platform data in users.

Risks: many behavior differences are data-driven by large settings tables, so incorrect register masks or IDs affect multiple files. The inline locked helpers serialize page-sensitive regmap accesses but callers that directly use regmap must manage page state. External sensors are represented in the same enable/FIFO masks as internal sensors, making ID boundaries important.

Test signals: compile coverage across core/buffer/shub/bus modules, all supported device IDs matching settings entries, mount-matrix ext info exposure, sensor enable dispatch for internal vs external IDs, and lockdep coverage around page/fifo/conf locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx.h -->
