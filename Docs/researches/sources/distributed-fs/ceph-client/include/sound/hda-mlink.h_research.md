# sources/distributed-fs/ceph-client/include/sound/hda-mlink.h

## Purpose
This header declares Intel HD-audio extended multi-link management helpers used by SOF/HDA systems, with no-op stubs when the feature is disabled.

## Important APIs, Types, and Functions
When `CONFIG_SND_SOC_SOF_HDA_MLINK` is enabled it declares initialization/free, extended-link count, interrupt enable/check, sync period programming, sync prepare/go/check, power up/down, SoundWire sublink helpers, LSDIID get/set, stream-channel mapping, put/reset/resume/suspend, hlink getters for SSP/DMIC/SoundWire, mutex access, offload enable, and ACE3+ microphone privacy helpers. Disabled builds provide inline stubs returning success, false, NULL, or doing nothing.

## Control Flow
HDA/SOF bus setup initializes multi-link state, powers up/down extended links around usage, maps SoundWire stream channels, coordinates synchronization, and handles privacy/offload/link interrupts. Callers can compile unconditionally and rely on stubs if the feature is off.

## State and Persistence
State lives in `struct hdac_bus` and `struct hdac_ext_link` implementation internals. Power/sync/privacy/link state is hardware-backed and must be managed during runtime/system PM. This header stores no state.

## Dependencies and Integration Points
It forward-declares HDA bus/link types and integrates with SOF HDA, SoundWire, SSP, DMIC, HD-audio extended link power management, and microphone privacy controls.

## Risks and Edge Cases
The stub behavior mostly returns success, which can hide disabled-feature paths if callers expect actual hardware action. Functions with `_unlocked` suffix require external locking, and misuse can race link power/sync state. Privacy state is platform-specific and needs careful event handling.

## Test Signals
Builds with config enabled/disabled, link power sequencing, SoundWire stream mapping, sync-go timing, suspend/resume, interrupt handling, offload enable/disable, and mic privacy event tests are key.
