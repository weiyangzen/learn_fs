# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-subdev-priv.h

## Purpose
`v4l2-subdev-priv.h` is a small private header for V4L2 subdevice core internals. It exposes privacy LED acquire/release helpers to core files without making them part of the public media header API.

## Important APIs, Types, And Functions
It declares `int v4l2_subdev_get_privacy_led(struct v4l2_subdev *sd)` and `void v4l2_subdev_put_privacy_led(struct v4l2_subdev *sd)`. The implementation is in `v4l2-subdev.c`.

## Control Flow
There is no runtime control flow in this header. Including files can call the get helper during subdev setup and the put helper during teardown. The implementation acquires an LED named `privacy`, disables user sysfs control while owned, and restores access on release when LED class support is reachable.

## State And Persistence
The declared helpers operate on `sd->privacy_led`. The header itself owns no state and stores no data.

## Dependencies And Integration Points
The header assumes `struct v4l2_subdev` is visible to including code through surrounding V4L2 headers. It is intentionally private to `drivers/media/v4l2-core`.

## Risks And Test Signals
The main risk is accidental public use or include-order breakage if included without a visible `struct v4l2_subdev` declaration. Build coverage with LED class enabled, modular, and disabled configurations is the primary test signal.
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-subdev-priv.h

## Purpose
`v4l2-subdev-priv.h` is a small private header for V4L2 subdevice core internals. It exposes privacy LED acquire/release helpers to core files without making them part of the public media header API.

## Important APIs, Types, And Functions
It declares `int v4l2_subdev_get_privacy_led(struct v4l2_subdev *sd)` and `void v4l2_subdev_put_privacy_led(struct v4l2_subdev *sd)`. The implementation is in `v4l2-subdev.c`.

## Control Flow
There is no runtime control flow in this header. Including files can call the get helper during subdev setup and the put helper during teardown. The implementation acquires an LED named `privacy`, disables user sysfs control while owned, and restores access on release when LED class support is reachable.

## State And Persistence
The declared helpers operate on `sd->privacy_led`. The header itself owns no state and stores no data.

## Dependencies And Integration Points
The header assumes `struct v4l2_subdev` is visible to including code through surrounding V4L2 headers. It is intentionally private to `drivers/media/v4l2-core`.

## Risks And Test Signals
The main risk is accidental public use or include-order breakage if included without a visible `struct v4l2_subdev` declaration. Build coverage with LED class enabled, modular, and disabled configurations is the primary test signal.
