# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_midi.c

Purpose: creates BeBoB ALSA rawmidi devices and connects rawmidi open/close/trigger operations to the shared duplex AMDTP stream.

Important APIs/functions: `midi_open`, `midi_close`, `midi_capture_trigger`, `midi_playback_trigger`, `set_midi_substream_names`, and `snd_bebob_create_midi_devices`.

Control flow and state: open obtains the stream lock, reserves duplex resources at the current rate, increments `substreams_counter`, and starts streaming. Close decrements the counter, stops duplex streaming when last user exits, and releases the lock. Trigger installs or clears the rawmidi substream pointer in the AM824 TX/RX stream under spinlock.

Dependencies/integration: depends on `snd_bebob_stream_*`, AM824 MIDI trigger support, ALSA rawmidi, and detected `midi_input_ports`/`midi_output_ports`. Risks include substream counter imbalance if start fails, shared stream contention with PCM and hwdep locks, and port count discovery errors. Test signals are rawmidi device creation only when ports exist, duplex flags when both directions exist, and MIDI byte transfer during active streams.
