# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-protocol-v2.c

## Purpose

This file implements MOTU protocol version 2 for 828mk2, 896HD, Traveler, UltraLite, and 8pre. It handles the shared v2 clock register, optical interface configuration, model-specific frame fetching bits, packet-format detection, and model spec definitions.

## Important APIs, types, and functions

The exported v2 protocol functions implement clock get/set/source, fetching-mode switching, and packet-format caching. `get_clock_rate()` decodes the clock-rate index into `snd_motu_clock_rates`. `get_clock_source()` maps hardware source bits into generic clock enums and consults the I/O configuration register for S/PDIF-on-optical detection. `switch_fetching_mode_cyclone()` and `switch_fetching_mode_spartan()` encode FPGA-family quirks.

## Control flow

Set-rate searches the common rate table, read-modify-writes `V2_CLOCK_STATUS_OFFSET`, and rejects unknown rates. Fetching mode is a no-op for 828mk2 and 896HD but updates `V2_CLOCK_FETCH_ENABLE` and sometimes `V2_CLOCK_MODEL_SPECIFIC` for Traveler/UltraLite/8pre. Packet-format caching reads `V2_IN_OUT_CONF_OFFSET`, copies fixed chunks, and adds ADAT-derived chunks depending on enabled input/output optical modes.

## State and persistence behavior

The file writes persistent hardware clock/fetch bits and refreshes in-memory packet-format caches. It does not own allocation or ALSA state.

## Dependencies and integration points

It is called through inline dispatchers in `motu.h` from PCM open, stream reserve/start, and proc reads. Register access is through `motu-transaction.c`; output constraints depend on the cached chunk arrays.

## Risks and test signals

Risks include hardware-family quirks being underdocumented, S/PDIF source ambiguity, and incorrect chunk additions for the dual-optical 8pre. Tests should cover each model spec, all supported rates, optical ADAT/S/PDIF transitions, external clock sources, and fetching-mode behavior at double-rate SPH.
