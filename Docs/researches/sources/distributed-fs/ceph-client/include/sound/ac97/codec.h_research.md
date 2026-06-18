# sources/distributed-fs/ceph-client/include/sound/ac97/codec.h

## Purpose

`codec.h` defines the newer AC97 codec bus-facing device and driver abstractions used by AC97 codec drivers and controllers.

## Important APIs, Types, and Functions

`AC97_ID()` combines two 16-bit vendor ID words into one 32-bit ID. `AC97_DRIVER_ID()` creates an `struct ac97_id` match entry with mask and private data. `struct ac97_codec_device` embeds `struct device` and stores vendor ID, codec number, BIT_CLK pointer, and owning AC97 controller. `struct ac97_codec_driver` embeds `struct device_driver` and supplies `probe`, `remove`, optional `shutdown`, and an ID table.

Helpers include `to_ac97_device()`, `to_ac97_driver()`, `ac97_codec_dev2dev()`, `ac97_get_drvdata()`, `ac97_set_drvdata()`, and `snd_ac97_codec_get_platdata()`. `snd_ac97_codec_driver_register()` and `_unregister()` are real only with `CONFIG_AC97_BUS_NEW`; otherwise they are no-op stubs.

## Control Flow

The AC97 bus instantiates codec devices on an AC-link, senses vendor IDs, matches drivers through masked ID tables, and invokes driver callbacks. Driver state is stored in the embedded device drvdata.

## State and Persistence

Codec device state includes vendor ID, link slot number, clock pointer, controller pointer, and driver data. Lifetime is managed by the Linux driver core and AC97 bus.

## Dependencies and Integration Points

The header depends on Linux device infrastructure and forward declarations for AC97 controller and clocks. It integrates ALSA AC97 codec drivers with AC97 digital controllers and platform data.

## Risks

Incorrect ID masks can bind the wrong codec. Disabled-config no-op registration can hide missing bus support. Embedded device lifetime and drvdata cleanup must match probe/remove ordering.

## Test Signals

Test ID/mask matching, enabled driver registration/unregistration, disabled-config compilation, probe/remove/shutdown ordering, platform data retrieval, and multiple codec numbers on one AC-link.
