# sources/distributed-fs/ceph-client/sound/ac97/bus.c

## Purpose

This file implements the new AC97 controller/codec bus. It lets digital controllers register available codec slots, scans AC97 vendor IDs, creates codec devices, matches codec drivers by ID table, exposes reset operations through sysfs, and handles runtime PM and codec clocks.

## Important APIs, types, and functions

Public exports include `snd_ac97_codec_driver_register`, `snd_ac97_codec_driver_unregister`, `snd_ac97_codec_get_platdata`, `snd_ac97_controller_register`, `snd_ac97_controller_unregister`, `snd_ac97_bus_scan_one`, and `ac97_bus_type`. Internal state includes `ac97_controllers_mutex`, `ac97_adapter_idr`, and `ac97_controllers`. Important callbacks include `ac97_codec_release`, `ac97_codec_add`, `ac97_bus_scan`, `cold_reset_store`, `warm_reset_store`, `ac97_add_adapter`, `ac97_del_adapter`, `ac97_pm_runtime_suspend`, `ac97_pm_runtime_resume`, `ac97_bus_match`, `ac97_bus_probe`, and `ac97_bus_remove`.

## Control Flow

A controller registration allocates an `ac97_controller`, copies optional per-codec platform data, registers an adapter device, resets the bus, and scans available slots. Scanning reads vendor ID registers through controller ops and creates `ac97_codec_device` children. Driver matching rejects invalid IDs and walks the codec driver's ID table with masked comparisons. Probe enables an `ac97_clk`, activates runtime PM, and invokes the codec driver's probe; failure unwinds PM and clock state. Removal resumes the device, calls driver remove, disables the clock, and disables runtime PM.

## State and Persistence

Controllers are tracked in an IDR and global list under a mutex. Each controller owns codec pointers by slot, platform data, parent device, adapter device, and ops. Codec devices persist in the driver model until unregistered; device release clears the controller slot and frees OF node references. Runtime PM and clock state are tied to bound codec devices.

## Dependencies and Integration Points

It depends on Linux driver core, OF child matching, IDR, mutexes, clocks, PM runtime, sysfs attributes, and AC97 public headers. Controller drivers call the exported register API; codec drivers register on `ac97_bus_type`.

## Risks and Test Signals

Risks include controller lifetime races with codec devices, sysfs reset while drivers are active, missing controller ops checks, clock/PM imbalance on probe/remove errors, OF child compatibility matching errors, and ignored `ac97_bus_scan()` return from registration. Tests should cover multi-slot probing, invalid IDs, masked driver matching, probe failure unwind, runtime suspend/resume, controller unregister with bound codecs, and sysfs reset paths.
