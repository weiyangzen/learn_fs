# sources/distributed-fs/ceph-client/sound/aoa/soundbus/soundbus.h

## Purpose
This header defines the generic Apple Onboard Audio soundbus abstraction used between bus providers such as I2S and codec/fabric drivers. It describes codec capabilities, codec callbacks, soundbus devices, soundbus drivers, and sysfs-visible device attributes.

## Important APIs, Types, And Functions
`enum clock_switch` defines multi-phase notifications for clock master/slave transitions. `struct transfer_info` describes usable codec transfer formats, rates, direction, clock-source requirement, and a tag. `struct codec_info` is the codec driver callback table and includes transfer descriptions, sysclock/bus factors, clock switching, usability, open/close, prepare/start/stop, suspend, and resume. `struct soundbus_dev` wraps a platform device, modalias, PCM naming/id fields, PCM pointer, attach/detach operations, codec list, and direction flags. `struct soundbus_driver` wraps a Linux `device_driver` with soundbus probe/remove/shutdown callbacks. External APIs include soundbus device add/remove/get/put and driver register/unregister.

## Control Flow
Bus providers fill a `soundbus_dev`, register it with `soundbus_add_one()`, and implement `attach_codec()`/`detach_codec()`. Codec or fabric drivers register a `soundbus_driver`, probe matching soundbus devices by policy outside this header, and attach codec descriptions that the provider uses to create PCM streams and call lifecycle callbacks.

## State And Persistence
The soundbus device persists as a platform device plus provider-owned codec list. Codec attachments persist as provider-private `codec_info_item` entries. `pcmid`, `pcmname`, and `pcm` tie the abstract soundbus to an ALSA card/PCM object. `have_out` and `have_in` are provider-private direction availability flags.

## Dependencies And Integration Points
The header depends on Linux platform devices and lists, ALSA PCM types, module ownership, and power-management message types through included sound headers. It is used by the AOA soundbus core, sysfs attributes, I2S bus provider, and codec drivers.

## Risks And Test Signals
The contract relies on codec callbacks observing context rules, especially atomic `start()` and `stop()`. Multiple codecs on one bus must agree on clock factors unless the provider explicitly supports per-transfer clocking. Test signals include correct modalias matching, attach/detach reference handling, callback order during prepare/start/stop/suspend/resume, and clean behavior when codec callback pointers are optional.
