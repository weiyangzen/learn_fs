# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-i2c-core.h

Purpose: small lifecycle header for the pvrusb2 I2C core. It exposes the adapter setup and teardown functions to the hardware core while keeping transfer implementation private.

Important APIs, types, and functions: forward declares `struct pvr2_hdw`; declares `pvr2_i2c_core_init(struct pvr2_hdw *)` and `pvr2_i2c_core_done(struct pvr2_hdw *)`.

Control flow: `pvrusb2-hdw.c` calls `pvr2_i2c_core_init()` after FX2 firmware/powerup is ready and before V4L2 subdevices are loaded. It calls `pvr2_i2c_core_done()` during disconnect to unregister the adapter and clients.

State and persistence: this header defines no state. The implementation stores adapter, algorithm, callback table, and IR state inside `struct pvr2_hdw`.

Dependencies and integration points: isolates I2C lifecycle from public hardware APIs and lets hardware initialization avoid exposing Linux I2C details to unrelated callers.

Risks: callers must only initialize once per connected hardware object and must call done before USB memory/parent device references disappear. Reordering around subdevice creation/removal risks dangling I2C clients.

Test signals: probe/remove cycle with subdevices loaded; unplug during initialization; build coverage for all files including this header; no I2C adapter leaks after disconnect.
