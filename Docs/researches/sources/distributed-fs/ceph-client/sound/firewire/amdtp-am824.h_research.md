# sources/distributed-fs/ceph-client/sound/firewire/amdtp-am824.h

Purpose: declares the AM824 protocol interface used by FireWire ALSA subdrivers that transport PCM and MIDI over AMDTP streams.

Important APIs, types, and functions: the header defines `AM824_IN_PCM_FORMAT_BITS` and `AM824_OUT_PCM_FORMAT_BITS` as `SNDRV_PCM_FMTBIT_S32`, maximum PCM channels as 64, and maximum MIDI conformant data channels as 1. It declares parameter setup, PCM/MIDI position mapping, PCM hardware constraints, MIDI trigger, and stream initialization functions.

Control flow: a subdriver includes this header, initializes an `amdtp_stream` with `amdtp_am824_init()`, configures stream parameters before start, calls position setters for device-specific channel maps, applies constraints from PCM open/prepare paths, and calls `amdtp_am824_midi_trigger()` from rawmidi trigger callbacks.

State and persistence: the header exposes no state directly. State is hidden in the protocol allocation created by `amdtp_am824_init()` and accessed through the declared functions.

Dependencies and integration: includes ALSA PCM/rawmidi headers and `amdtp-stream.h`. It binds device-family drivers to the common AMDTP scheduler while hiding AM824 payload internals.

Risks: constants are part of the subdriver contract; increasing MIDI conformant channel support or PCM format support requires coordinated implementation changes in `amdtp-am824.c`. Test signals include compile coverage for all subdrivers including this header, parameter validation against the documented maximums, and PCM format constraints matching S32-only behavior.
