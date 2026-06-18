# sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-midi.c

Purpose: creates rawmidi devices for Digi00x physical MIDI ports and optional console/control-surface MIDI ports, wiring them to the DOT AMDTP streams.

Important APIs/functions: `midi_open`, `midi_close`, `midi_capture_trigger`, `midi_playback_trigger`, `set_substream_names`, `add_substream_pair`, and `snd_dg00x_create_midi_devices`.

Control flow and state: open locks and starts the shared duplex stream, increments `substreams_counter`, and unwinds on failure. Close decrements the counter, stops streams as needed, and releases the lock. Triggers map rawmidi device 0 substreams to physical ports and nonzero device to port 2 for console/control, then install or clear DOT MIDI substream pointers under spinlock. Creation always adds physical ports and adds console ports only for console models.

Dependencies/integration: depends on Digi00x stream management, DOT MIDI trigger support, ALSA rawmidi, and `is_console`. Risks include label/name inversion in `add_substream_pair` making UI names confusing, port 2 multiplexing assumptions, and substream counter handling on start failure. Test signals are expected rawmidi devices for rack versus console models and MIDI transfer on physical and control ports.
