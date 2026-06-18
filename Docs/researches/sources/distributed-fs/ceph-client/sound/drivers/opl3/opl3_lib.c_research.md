# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_lib.c

## Purpose
Provides the common ALSA OPL2/OPL3/OPL4 FM chip library: low-level register writes, chip detection, hardware timer exposure, codec object lifetime, and hwdep/sequencer device registration.

## Important APIs, Types, And Functions
Exports `snd_opl3_new()`, `snd_opl3_init()`, `snd_opl3_create()`, `snd_opl3_timer_new()`, `snd_opl3_hwdep_new()`, and `snd_opl3_interrupt()`. Internal helpers include `snd_opl2_command()`, `snd_opl3_command()`, `snd_opl3_detect()`, and timer start/stop routines for FM timer 1 and timer 2.

## Control Flow
Callers create an OPL3 object with ports and hardware type. The library optionally reserves I/O regions, chooses an OPL2-style or OPL3-style command function, detects chip type through the FM timer status sequence when auto-detecting, initializes OPL3 mode for capable chips, and registers an ALSA codec device. `snd_opl3_hwdep_new()` exposes a direct FM hwdep device and, when sequencer support is enabled, creates an OPL3 sequencer device carrying the `struct snd_opl3 *`. Interrupts inspect the FM status register and notify ALSA timers.

## State And Persistence
Runtime state includes port resources, hardware type, max voice count, timer enable bits, locks, hwdep pointer, and optional sequencer device pointer. There is no persistent storage.

## Dependencies And Integration
Uses raw I/O port access, ALSA card/device/hwdep/timer/sequencer APIs, and OPL register constants. OPL4 creation reuses this library for the FM half, passing integrated ports to avoid duplicate resource ownership.

## Risks And Test Signals
Detection depends on timer behavior that some integrated hardware does not implement, hence special hardware cases bypass detection. Resource-release ordering is important because failures call `snd_device_free()`. Tests should build with/without sequencer and OSS, probe OPL2/OPL3/OPL4 hardware types, exercise hwdep ioctls, verify timer interrupts, and test duplicate I/O region rejection.
