# sources/distributed-fs/ceph-client/include/sound/ac97/compat.h

## Purpose

`compat.h` bridges the newer `struct ac97_codec_device` bus model to the legacy ALSA `struct snd_ac97` representation.

## Important APIs, Types, and Functions

It includes `<sound/ac97_codec.h>` for the legacy type and declares `snd_ac97_compat_alloc(struct ac97_codec_device *adev)` plus `snd_ac97_compat_release(struct snd_ac97 *ac97)`.

## Control Flow

Code allocates a compatibility object for a new AC97 codec device, passes it to legacy AC97 paths, and releases it when the codec is removed or compatibility use ends.

## State and Persistence

State lives in the allocated legacy `snd_ac97` compatibility object and any legacy ALSA state attached to it. The header itself stores nothing.

## Dependencies and Integration Points

It depends on legacy ALSA AC97 declarations and the newer AC97 codec-device model. It is the integration point for old AC97 codec/controller code that has not moved fully to the new bus.

## Risks

Risks include lifetime mismatches between `snd_ac97` and the underlying codec device, double release, and incomplete initialization for legacy users.

## Test Signals

Test allocation and release around codec probe/remove, representative legacy AC97 operations, leak/double-free checks, and build coverage for old/new AC97 configurations.
