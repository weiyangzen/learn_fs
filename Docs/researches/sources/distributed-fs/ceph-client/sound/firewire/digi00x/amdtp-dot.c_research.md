# sources/distributed-fs/ceph-client/sound/firewire/digi00x/amdtp-dot.c

Purpose: implements the Digi 002/003 custom AMDTP "DOT" protocol for PCM and MIDI payload processing on top of generic AMDTP streams.

Important APIs/functions: `amdtp_dot_init`, `amdtp_dot_set_parameters`, `amdtp_dot_reset`, `amdtp_dot_add_pcm_hw_constraints`, `amdtp_dot_midi_trigger`, and payload callbacks `process_ir_ctx_payloads`/`process_it_ctx_payloads`. Internal helpers include the reverse-engineered `dot_scrt`/`dot_encode_step`, PCM read/write/silence routines, MIDI packet read/write, and FIFO rate limiting.

Control flow and state: initialization selects incoming or outgoing payload callback and uses `CIP_NONBLOCKING | CIP_UNAWARE_SYT`. Parameter setup reserves one MIDI data channel plus PCM channels, sets AM824 FDF, records PCM channel count, and computes MIDI FIFO limits. Outgoing processing writes PCM or silence, applies the DOT byte-encoding state, and embeds MIDI bytes with port tags. Incoming processing copies PCM to ALSA buffers and dispatches MIDI bytes. `amdtp_dot_reset` clears encoder carry/index/offset state.

Dependencies/integration: uses generic AMDTP, ALSA PCM/rawmidi, `amdtp_rate_table`, and Digi00x stream code. Risks include protocol reverse-engineering assumptions, MIDI FIFO approximation, port tag handling for console MIDI, and buffer wrap logic. Test signals are clean 24-bit PCM playback/capture, no MIDI overruns, correct console/physical MIDI routing, and no artifacts after reset/start.
