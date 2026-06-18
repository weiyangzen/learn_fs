# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-midi.c

Purpose: creates DICE ALSA rawmidi devices and maps rawmidi operations to MIDI channels carried in AM824 streams.

Important APIs/functions: `midi_open`, `midi_close`, `midi_capture_trigger`, `midi_playback_trigger`, `set_midi_substream_names`, and `snd_dice_create_midi`.

Control flow and state: creation scans all streams for maximum input/output MIDI ports, creates one rawmidi device if any exist, and sets duplex flags. Open locks and starts the shared duplex stream at current rate. Close decrements `substreams_counter` and stops when no users remain. Trigger installs rawmidi substreams on stream 0 AM824 MIDI ports.

Dependencies/integration: uses DICE stream reserve/start/stop and AM824 MIDI trigger support. Risks include only routing MIDI through stream 0 despite `MAX_STREAMS`, substream counter imbalance, and detector-provided port counts exceeding actual AM824 capability. Test signals are rawmidi port counts matching formation data and MIDI transfer while PCM is idle or active.
