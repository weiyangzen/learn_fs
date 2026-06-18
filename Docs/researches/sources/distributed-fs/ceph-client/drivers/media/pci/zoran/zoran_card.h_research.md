# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_card.h

## Purpose
`zoran_card.h` exposes the small cross-file API owned by `zoran_card.c`. It defines the maximum number of supported cards and declares the video template, JPEG settings validation, default parameter initialization, video-device release, and the ZR36016 write helper needed outside the card file.

## Important APIs, Types, And Functions
`BUZ_MAX` is set to 4 and sizes the `card[]` and `video_nr[]` module parameter arrays. Extern declarations include `zoran_template`, `zoran_check_jpg_settings()`, `zoran_open_init_params()`, `zoran_vdev_release()`, and `zr36016_write()`.

## Control Flow
This header has no runtime flow, but it connects `zoran_driver.c` to the card layer. The V4L2 driver file uses `zoran_template`, `zoran_vdev_release()`, and settings validation/defaults. `zoran_device.c` calls `zr36016_write()` during JPEG start for old DC10/DC30-style ZR36016 plus ZR36050 pipelines.

## State And Persistence
No state is stored here. `BUZ_MAX` affects module-parameter array capacity and therefore limits runtime card instances to four.

## Dependencies And Integration Points
The prototypes rely on `struct zoran`, `struct zoran_jpg_settings`, `struct video_device`, and `struct videocodec` being visible through includers. It is included by `zoran_card.c`, `zoran_device.c`, and `zoran_driver.c`.

## Risks
The `BUZ_MAX` hard cap is noted as "Anybody who uses more than four?" and could reject additional PCI devices in multi-card systems. Exposing `zr36016_write()` is described in the C file as a hack for `zoran_device.c`, signaling tight coupling between the VFE codec and device engine.

## Test Signals
Build coverage confirms prototypes and include ordering. Runtime multi-card tests beyond four devices should fail predictably. DC30/DC10 paths using ZR36016 should exercise the exported write helper during JPEG start.
