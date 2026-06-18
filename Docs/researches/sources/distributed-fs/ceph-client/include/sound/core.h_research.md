# sources/distributed-fs/ceph-client/include/sound/core.h

## Purpose
`core.h` is the main ALSA kernel core contract. It defines sound-card objects, child-device lifecycle management, device/minor registration, card allocation/registration/free paths, control storage, file tracking, power references, DMA helpers, PCI quirk helpers, debug macros, and async notification helpers.

## Important APIs, Types, and Functions
Core types are `enum snd_device_type`, `enum snd_device_state`, `struct snd_device_ops`, `struct snd_device`, `struct snd_card`, `struct snd_minor`, and `struct snd_pci_quirk`. Major APIs include `snd_card_new()`, `snd_devm_card_new()`, `snd_card_register()`, `snd_card_disconnect()`, `snd_card_free()`, `snd_device_new()`, device register/disconnect/free helpers, `snd_register_device()`, `snd_unregister_device()`, `snd_lookup_minor_data()`, card file add/remove, power wait/ref helpers, ISA DMA helpers, PCI quirk lookup, and fasync helpers.

## Control Flow
Drivers allocate a card, create child devices with ordered `snd_device_type`, register all devices, and later disconnect/free them in controlled order. File tracking and `shutdown` prevent new operations during removal. PM helpers manage card power state and wait for in-flight references.

## State and Persistence Behavior
`struct snd_card` owns persistent runtime state for a sound card: names, devices, controls, proc/debugfs roots, open files, sysfs device, memory accounting, PM state, and optional OSS mixer data. It persists until card free; no state survives driver unload except hardware/firmware side effects.

## Dependencies and Integration Points
It depends on Linux device, mutex/rwsem, PM, printk, xarray, debugfs, file, DMA, PCI, and ALSA UAPI constants. Almost every ALSA subsystem includes it.

## Risks and Test Signals
Risks include lifecycle ordering bugs, stale minor private data, card removal races, power-ref leaks, control lookup collisions, and memory accounting drift. Test signals include card probe/remove, hot-unplug with open files, PM suspend/resume, minor lookup, child-device failure unwinding, and PCI quirk matching.
