# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v3.c

## Purpose

This file implements MOTU protocol version 3 for mk3/Hybrid/Audio Express/Track16/4pre models. It manages clock rate/source, waits for asynchronous clock-change notification, controls frame fetching, handles optical-interface-dependent packet formats, and declares v3 model specs.

## Important APIs, types, and functions

Exports mirror the protocol interface in `motu.h`: clock get/set/source, fetching switch, and packet-format cache. `snd_motu_protocol_v3_set_clock_rate()` writes the clock index and clears fetch mode before waiting up to four seconds for `V3_MSG_FLAG_CLK_CHANGED` on `hwdep_wait`. `detect_packet_formats_with_opt_ifaces()` adds ADAT or S/PDIF chunk counts for enabled optical interfaces.

## Control flow

Clock source decoding reads `V3_CLOCK_STATUS_OFFSET`; optical A/B sources require a second read of `V3_OPT_IFACE_MODE_OFFSET` to distinguish ADAT from S/PDIF. Fetching mode simply toggles `V3_FETCH_PCM_FRAMES`. Packet-format caching copies model fixed chunks, reads optical mode, and applies dynamic additions only for models with optical-dependent layouts.

## State and persistence behavior

The file writes clock/fetch registers and uses `motu->msg` as a transient notification latch. Packet-format cache mutations persist in `motu->tx_packet_formats` and `rx_packet_formats` until refreshed.

## Dependencies and integration points

It depends on MOTU transaction helpers, async message delivery in `motu-transaction.c`, wait queues in `struct snd_motu`, and stream startup in `motu-stream.c`. Command-DSP/register-DSP parser initialization in stream startup depends on model flags defined here.

## Risks and test signals

Risks include timeout or missed wakeup during clock changes, ambiguous unknown clock sources, and incorrect optical chunk math for hybrid models. Tests should exercise rate changes, bus-reset recovery after a pending wait, packet-format cache after optical mode changes, and all listed model specs.
