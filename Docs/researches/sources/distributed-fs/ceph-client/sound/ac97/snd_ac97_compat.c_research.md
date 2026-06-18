# sources/distributed-fs/ceph-client/sound/ac97/snd_ac97_compat.c

## Purpose

This file provides a compatibility wrapper that exposes a legacy `struct snd_ac97` object on top of a new `ac97_codec_device`, allowing older AC97/ASoC code paths to use new AC97 controller operations.

## Important APIs, types, and functions

Public exports are `snd_ac97_compat_alloc`, `snd_ac97_compat_release`, and a compatibility implementation of `snd_ac97_reset`. Internal bus ops are `compat_ac97_reset`, `compat_ac97_warm_reset`, `compat_ac97_write`, and `compat_ac97_read`, collected in `compat_snd_ac97_bus_ops` and `compat_soc_ac97_bus`.

## Control Flow

Allocation creates a zeroed `snd_ac97`, points private data at the new codec device, assigns a synthetic legacy AC97 bus, initializes a child device named with `-compat`, and registers it. Legacy read/write/reset callbacks translate through `adev->ac97_ctrl->ops`. Reset optionally tries warm reset first, rescans the slot via `snd_ac97_bus_scan_one()`, and accepts success if the scanned ID matches the codec vendor ID under the supplied mask; otherwise it performs cold plus warm reset and repeats the scan.

## State and Persistence

The compatibility `snd_ac97` persists as a registered child device until `snd_ac97_compat_release()`. It does not own the underlying controller or codec device; it stores the pointer in `private_data`.

## Dependencies and Integration Points

It depends on the new AC97 bus controller structures, legacy `<sound/ac97_codec.h>` semantics, ASoC AC97 callbacks, and the private `ac97_core.h` scan and ID helper. It is only built when `CONFIG_AC97_BUS_COMPAT` is enabled.

## Risks and Test Signals

Risks include lifetime mismatch between compat objects and underlying codec devices, missing controller ops, reset ID comparisons ignoring the `id` argument and using `adev->vendor_id`, and duplicate `snd_ac97_reset` when legacy AC97 is also built. Tests should cover allocation failure unwind, device release, warm reset success, cold reset success, masked ID mismatch, and controller unregister while compat objects exist.
