<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_bridge.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_bridge.h

Purpose: `m5602_bridge.h` is the shared private bridge header for ALi m5602 GSPCA webcam drivers. It defines bridge register addresses, endpoint constants, driver metadata, per-device state, and bridge/sensor I/O prototypes.

Important APIs, types, and functions: the header maps many `M5602_XB_*` and `M5602_OB_*` register constants for sensor geometry, clocks, endpoint control, I2C, GPIO, power, and scratch registers. It defines `I2C_BUSY`, module description strings, endpoint addresses `0x81` and `0x82`, and `M5602_URB_MSG_TIMEOUT`. `struct sd` embeds `gspca_dev`, stores the active `struct m5602_sensor *`, frame ID/count, optional rotation thread, and several V4L2 control clusters. Function prototypes cover bridge reads/writes and sensor reads/writes.

Control flow: no implementation lives here, but m5602 core/sensor files use these constants and prototypes to reset the bridge, configure the active image sensor, poll I2C state, stream isochronous data, and expose controls.

State and persistence: `struct sd` defines persistent per-device runtime state, including frame boundary tracking, active sensor dispatch, rotation polling, and clustered controls for white balance, exposure, gain, and flips.

Dependencies and integration points: includes `gspca.h` and Linux slab support. It depends on an external `struct m5602_sensor` definition from other m5602 headers/sources in the module and is built through the m5602 Makefile.

Risks: register constants are low-level hardware ABI; mistakes can break sensor setup or bus access. Control cluster pointers must be initialized consistently by the core. Test signals include successful sensor detection, I2C operations clearing `I2C_BUSY`, correct frame ID transitions, rotation handling on flip-capable cameras, and no unresolved references to bridge I/O helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_bridge.h -->
