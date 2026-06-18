# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-proc.c

## Purpose

This file adds `/proc/asound/.../firewire` information nodes for MOTU devices. It provides human-readable clock and packet-format diagnostics for users, developers, and regression triage.

## Important APIs, types, and functions

`snd_motu_proc_init()` creates a `firewire` directory under the ALSA card proc root. `proc_read_clock()` reports the current sample rate and decoded clock source using protocol-version helpers. `proc_read_format()` refreshes packet formats and prints message chunks, fixed chunks, and total PCM chunks per supported rate for transmit and receive directions. `clock_names[]` maps `enum snd_motu_clock_source` values to display strings.

## Control flow

Proc reads are best-effort: if any FireWire transaction or protocol parser fails, the callback returns without printing partial fallback data. Format output iterates all six MOTU clock rates and maps each rate to one of the three packet modes by `mode = i >> 1`.

## State and persistence behavior

The proc callbacks do not persist proc-local state, but `proc_read_format()` refreshes `motu->tx_packet_formats` and `motu->rx_packet_formats`, so reading the file can update cached packet-format state.

## Dependencies and integration points

It integrates with ALSA info entries, `motu.h`, and the version-specific protocol cache and clock functions. It depends on `motu->spec` fixed chunk arrays and cached dynamic packet formats.

## Risks and test signals

Risks include stale or failed hardware reads producing empty proc files and user-visible confusion if `clock_names` diverges from protocol enums. Useful tests are proc reads while idle, while streaming, after optical interface changes, and after bus reset.
