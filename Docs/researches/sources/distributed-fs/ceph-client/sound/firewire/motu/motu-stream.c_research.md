# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-stream.c

## Purpose

This file owns MOTU duplex isochronous streaming. It initializes AMDTP streams/resources, reserves channels and bandwidth, programs MOTU streaming registers, starts/stops the shared AMDTP domain, handles bus-generation updates, and exposes stream locks for ALSA/hwdep coordination.

## Important APIs, types, and functions

Public functions include `snd_motu_stream_init_duplex()`, `cache_packet_formats()`, `reserve_duplex()`, `start_duplex()`, `stop_duplex()`, `destroy_duplex()`, `lock_try()`, and `lock_release()`. Helpers program `ISOC_COMM_CONTROL_OFFSET` and `PACKET_FORMAT_OFFSET`, allocate resources in `keep_resources()`, and call `amdtp_motu_set_parameters()`.

## Control flow

Reserve stops active streaming when the first substream opens or rate changes, frees resources, sets hardware clock rate, refreshes packet formats, allocates tx/rx resources, sets domain period sizing, and allocates the MOTU cache ring. Start updates resources after bus reset, writes packet format flags, initializes DSP parsers when needed, registers tx/rx channels with the device, adds both streams to the AMDTP domain, initializes cache cursors, starts the domain, waits readiness, then enables device frame fetching. Stop tears all of that down only when the substream count reaches zero.

## State and persistence behavior

Persistent state includes FireWire resource reservations, hardware communication register state, AMDTP domain state, `cache.event_offsets`, and stream lock counters. `dev_lock_count < 0` is the user-space exclusive lock state; positive counts mean kernel PCM/MIDI users.

## Dependencies and integration points

It integrates `motu-transaction.c`, protocol dispatchers, `amdtp-motu`, `fw_iso_resources`, and ALSA PCM/MIDI callers. `motu_bus_update()` re-registers transactions; stream startup separately updates resource generations.

## Risks and test signals

Risks include partial resource allocation cleanup, cache allocation sizing, start-order sensitivity, and fetch-mode failures leaving hardware active. Test signals include bus reset during streaming, rate-change reopen, no-substream stop, external clock use, DSP parser init failures, and generation mismatch recovery.
