# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-stream.c

## Purpose

This file owns TASCAM duplex audio streaming: clock register handling, data-channel enablement, stream session programming, FireWire resource allocation, AMDTP domain startup/shutdown, bus-reset handling, and stream locks.

## Important APIs, types, and functions

Exports include `snd_tscm_stream_get_rate()`, `get_clock()`, `init_duplex()`, `reserve_duplex()`, `start_duplex()`, `stop_duplex()`, `update_duplex()`, and lock helpers. Helpers program `TSCM_OFFSET_*` registers for clock, channels, stream start, isochronous channels, multiplex mode, and options.

## Control flow

`get_clock()` retries while the hardware clock status is intermediate. Reserve stops existing streams, finishes the session, frees resources, sets clock rate, allocates tx/rx resources, sets domain period sizing, and records whether a long transmit skip is needed after rate change. Start updates resources after bus reset, sets stream formats/channels, begins the hardware session, adds rx and tx streams to the domain, chooses up to 16000 skip cycles after rate changes, starts the domain with sequence replay, and waits up to four seconds ready. Stop tears down only when no substreams remain.

## State and persistence behavior

The file persists hardware register state, FireWire resource reservations, domain state, and `need_long_tx_init_skip`. Lock state mirrors other FireWire drivers: negative for user lock, positive for active kernel users.

## Dependencies and integration points

It depends on `amdtp-tascam.c`, `fw_iso_resources`, model specs, transaction register constants, PCM/MIDI callers, and hwdep lock notifications.

## Risks and test signals

Risks include undocumented register writes, clock intermediate timeouts, cleanup after partial begin failures, and incorrect skip-cycle timing. Tests should cover all supported rates, bus reset, external clock, rate change while reopening, no-substream stop, and forced transaction failures.
