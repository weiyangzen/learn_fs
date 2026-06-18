# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-stream.c

## Purpose

This file discovers OXFW stream capabilities, parses AV/C AM824 stream formats, initializes CMP/AM824 streams, reserves resources, starts/stops the duplex AMDTP domain, and maintains stream locks.

## Important APIs, types, and functions

Exports include `snd_oxfw_stream_discover()`, `parse_format()`, `get_current_formation()`, `reserve_duplex()`, `start_duplex()`, `stop_duplex()`, `update_duplex()`, and lock helpers. `oxfw_rate_table[]` and `avc_stream_rate_table[]` translate between ALSA rates and AV/C FDF rate IDs. `fill_stream_formats()` reads LIST entries or falls back to `assume_stream_formats()`.

## Control flow

Discovery reads AV/C plug info, fills oPCR/iPCR format arrays, parses each format, and derives MIDI port counts. Reserve checks whether external software already owns CMP connections, compares requested formation with current formation, stops/breaks old connections when the formation changes, sets stream format, reserves CMP resources, and fixes domain period sizing. Start establishes CMP connections, adds streams to the domain, chooses skip-cycle/replay behavior by quirk, starts the domain, and waits ready. Bus reset stops the domain, breaks connections, and aborts PCM streams.

## State and persistence behavior

The file owns cached stream-format arrays, `has_input/has_output`, `assumed`, CMP connection state, AM824 stream state, `substreams_count`, and lock notifications. Device stream format and CMP plug state are persistent hardware-side until changed/reset.

## Dependencies and integration points

It depends on `oxfw-command.c`, `cmp`, AM824 helpers, FireWire generation tracking, and quirks from `oxfw.c`. PCM, MIDI, proc, and hwdep modules all rely on this stream contract.

## Risks and test signals

Risks include incorrect fallback assumptions, malformed format parsing, external CMP ownership conflicts, and quirk-specific SYT/DBC behavior. Test signals include LIST unsupported devices, all rate/channel entries, bus reset, JACK/FFADO coexistence, playback-only devices, jumbo payload devices, and voluntary recovery devices.
