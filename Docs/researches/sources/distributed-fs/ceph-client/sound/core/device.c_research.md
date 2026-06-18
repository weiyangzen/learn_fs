# sources/distributed-fs/ceph-client/sound/core/device.c

## Purpose
`device.c` implements the generic ALSA per-card device-component lifecycle. Drivers and core subsystems register components with a card, and the card lifecycle later registers, disconnects, and frees those components in a consistent order.

## Important APIs, Types, and Functions
Public APIs include `snd_device_new()`, `snd_device_register()`, `snd_device_disconnect()`, `snd_device_free()`, `snd_device_register_all()`, `snd_device_disconnect_all()`, and `snd_device_free_all()`. Internals include `look_for_dev()`, `__snd_device_register()`, `__snd_device_disconnect()`, and `__snd_device_free()`. Each `snd_device` records card, type, state, owner data pointer, and callback table `snd_device_ops`.

## Control Flow and State
`snd_device_new()` allocates a `snd_device`, sets state `SNDRV_DEV_BUILD`, and inserts it into `card->devices` sorted by device type. Registration calls `dev_register` only from BUILD state and transitions to REGISTERED. Disconnect calls `dev_disconnect` only from REGISTERED and transitions to DISCONNECTED. Free removes the node, disconnects if necessary, calls `dev_free`, and releases the wrapper. Bulk register walks forward; bulk disconnect and free walk reverse so later/higher-level devices are torn down before earlier foundations. `snd_device_free_all()` keeps CONTROL and LOWLEVEL devices until a second pass, preserving control and low-level cleanup ordering.

## Dependencies and Integration Points
The file is a core dependency for card init/free logic and subsystems such as hwdep, jack, PCM, rawmidi, and controls. It assumes `device_data` pointers uniquely identify components for lookup.

## Risks and Test Signals
Risks include duplicate `device_data`, wrong type ordering, callbacks that fail during registration/disconnect/free, and drivers calling free/disconnect for unknown devices. Tests should register mock components with ordered types, validate callback ordering and state transitions, inject registration failures, and verify card free leaves CONTROL/LOWLEVEL until the final cleanup pass.
