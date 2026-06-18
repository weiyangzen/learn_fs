# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-i2c.h

## Purpose
`ivtv-i2c.h` declares the ivtv I2C bus and subdevice registration API used by driver probe, EEPROM/card processing, and hardware lookup paths.

## Important APIs, Types, and Functions
It declares `ivtv_i2c_new_ir_legacy()`, `ivtv_i2c_register()`, `ivtv_find_hw()`, `init_ivtv_i2c()`, and `exit_ivtv_i2c()`.

## Control Flow
The header itself has no control flow. `ivtv-driver.c` initializes the adapter, scans/registers hardware bits through `ivtv_i2c_register()`, optionally probes legacy IR, looks up controlling subdevs with `ivtv_find_hw()`, and tears the adapter down on failure or remove.

## State and Persistence
The declared functions mutate I2C adapter/client state, V4L2 subdevice lists, hardware flags, and IR init data in `struct ivtv`; the header stores no state.

## Dependencies and Integration Points
It depends on `struct ivtv` and `struct v4l2_subdev` declarations from the core media stack. It bridges card hardware descriptors to Linux I2C and V4L2 subdevice registration.

## Risks and Edge Cases
Callers must initialize card descriptors and options before `init_ivtv_i2c()` and must not call registration helpers after adapter deletion. `ivtv_find_hw()` requires exact hardware bit masks matching subdevice `grp_id`.

## Test Signals
Build coverage should verify prototype consistency. Runtime tests should confirm adapter creation/removal, subdevice registration from every card hardware bit, legacy IR probing, and successful lookup of video/audio/muxer subdevices after probe.
