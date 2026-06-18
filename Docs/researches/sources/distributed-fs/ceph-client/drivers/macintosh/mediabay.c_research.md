# sources/distributed-fs/ceph-client/drivers/macintosh/mediabay.c

Purpose: manages hot-swappable media bays on classic PowerBooks. It polls bay content, sequences power/reset/bus enable for floppy, ATA CD, PCI, and sound devices, and notifies MacIO child drivers when bay state changes.

Important APIs and functions: `struct media_bay_info` holds per-bay state; `struct mb_ops` abstracts Ohare, Heathrow, and KeyLargo register operations. Exported helpers are `check_media_bay()`, `lock_media_bay()`, and `unlock_media_bay()`. `media_bay_step()` is the state machine; `media_bay_task()` polls every `MB_POLL_DELAY`; `media_bay_attach()`, suspend, and resume are the MacIO driver callbacks.

Control flow: attach reserves MacIO resources, maps the ASIC register base, picks ops from OF match data, initializes hardware, forces an empty detect, then starts one polling kthread. The poller locks each bay, reads debounced content, powers up/down when stable content changes, steps through power-up, bus enable, reset release, optional IDE reset wait, and `mb_up`. Hotplug is modeled by calling child drivers' `mediabay_event()` callback.

State and persistence: static `media_bays[MAX_BAYS]`, `media_bay_count`, per-bay content/state/timers, cached GPIO, sleep flag, and user lock. State is runtime-only and reconstructed on boot/probe.

Dependencies and integration: depends on MacIO, PMac feature/register definitions for Ohare/Heathrow/KeyLargo, PMU/ADB headers, kthreads, and `asm/mediabay.h` content IDs.

Risks: global bay array has no explicit overflow guard if firmware exposes more than `MAX_BAYS`. Poll timing is hardware-sensitive. `check_media_bay()` intentionally returns unlocked fuzzy snapshots. The kthread handle is not stored for later stop in this file. Suspend/resume paths rely on content remaining unchanged.

Test signals: insertion/removal debouncing, state transitions with correct delays, ATA reset timing, child `mediabay_event()` callbacks, suspend/resume with unchanged and changed content, exported helper behavior under lock, and old-machine register programming for all three ops tables.
