# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_stream.c

Purpose: implements BeBoB stream discovery, clock/rate access, CMP connection setup, AMDTP parameterization, duplex start/stop/reserve, and stream lock state.

Important APIs/functions: `snd_bebob_stream_get_rate`, `snd_bebob_stream_set_rate`, `snd_bebob_stream_get_clock_src`, `snd_bebob_stream_discover`, `snd_bebob_stream_init_duplex`, `snd_bebob_stream_reserve_duplex`, `snd_bebob_stream_start_duplex`, `snd_bebob_stream_stop_duplex`, `snd_bebob_stream_destroy_duplex`, `snd_bebob_stream_lock_try/release`, plus helpers for formation parsing, channel mapping, MIDI detection, and sync input discovery.

Control flow and state: discovery reads BridgeCo plug info, stream format entries, external MIDI plugs, and optional MSU sync input. Reserve checks for external CMP use, gets/sets rate, reserves both CMP connections, configures AM824 streams, and records period/buffer events. Start establishes both CMP connections, adds streams to the AMDTP domain, starts packet processing with replay and quirk-specific skip cycles, optionally reasserts M-Audio special rate, then waits for readiness. Stop tears down domain/CMP/resources when `substreams_counter` reaches zero.

Dependencies/integration: uses AV/C helpers, CMP, AM824, FireWire ISO resources, PCM/MIDI counters, and vendor specs. Risks include channel-position parsing, external applications holding CMP connections, devices needing both connections, DBC quirks, long startup delays, and rate changes while clients are open. Test signals are successful stream discovery, no cache mismatch, duplex readiness, correct MIDI/PCM maps, and stable bus-reset/XRUN recovery.
