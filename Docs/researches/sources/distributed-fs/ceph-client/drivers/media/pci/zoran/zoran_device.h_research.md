# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_device.h

## Purpose
`zoran_device.h` declares the low-level hardware operations implemented by `zoran_device.c` and provides convenience macros for calling the attached V4L2 decoder and encoder subdevices.

## Important APIs, Types, And Functions
Declarations cover GPIO access, guest-bus post-office reads/writes, JPEG codec sleep/reset, raw memory grabbing, interrupt helpers, JPEG start/enable/feed, PCI mastering, hardware initialization, and restart. It also declares `zoran_formats[]` and `pass_through`. Macros `decoder_call()` and `encoder_call()` wrap `v4l2_subdev_call()` on `zr->decoder` and `zr->encoder`.

## Control Flow
The header itself is declarative. Its API is used by `zoran_card.c` during probe/init/remove and by `zoran_driver.c` during vb2 streaming transitions. The subdevice call macros are used to route standards, inputs, streams, and encoder output paths.

## State And Persistence
No state is stored in the header. The declared functions mutate `struct zoran` and hardware registers. `pass_through` is a module-level runtime setting declared here for cross-file access.

## Dependencies And Integration Points
The header assumes visibility of `struct zoran`, `enum zoran_codec_mode`, `irqreturn_t`, and V4L2 subdevice types through includers. It is the boundary between user-facing vb2/V4L2 code and hardware register programming.

## Risks
The subdevice macros do not check whether `decoder` or `encoder` is NULL; callers rely on probe having created required subdevices or on `v4l2_subdev_call()` behavior. Because this API includes functions that must be called with locks held in some paths, call-site discipline is important and not encoded in types.

## Test Signals
Compile coverage across card/device/driver files validates declarations. Runtime signals are correct decoder/encoder routing, working raw/JPEG start/stop, interrupt handling, and behavior changes when `pass_through` is toggled.
