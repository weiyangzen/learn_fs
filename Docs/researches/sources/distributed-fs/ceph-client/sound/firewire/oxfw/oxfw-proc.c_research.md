# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-proc.c

## Purpose

This file adds a proc diagnostic node showing OXFW input/output stream formations and marking the currently active formation.

## Important APIs, types, and functions

`snd_oxfw_proc_init()` creates the `firewire/formation` ALSA info entry. `proc_read_formation()` reads the current input formation, iterates `rx_stream_formats`, and optionally repeats the process for output using `tx_stream_formats`. `add_node()` is a small info-entry helper.

## Control flow

The proc callback first reports "Input Stream to device" using `AVC_GENERAL_PLUG_DIR_IN`. If `has_output` is false it returns early. Otherwise it reports "Output Stream from device". Each row is parsed with `snd_oxfw_stream_parse_format()` and compared with the current formation using `memcmp()` to prefix an active row with `*`.

## State and persistence behavior

The file does not own durable state. Reads can trigger AV/C transactions through `snd_oxfw_stream_get_current_formation()`.

## Dependencies and integration points

It depends on OXFW stream discovery data and AV/C current-formation reads. The proc tree is removed automatically by ALSA card disconnect handling.

## Risks and test signals

Risks include empty output on transaction failure, misleading data if cached formats are stale, and `memcmp()` comparing padding if the formation structure changes. Test signals are proc output across all discovered formats, no-output devices, assumed-format devices, and active-format changes after PCM hw_params.
