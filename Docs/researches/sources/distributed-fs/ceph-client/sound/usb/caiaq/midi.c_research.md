# sources/distributed-fs/ceph-client/sound/usb/caiaq/midi.c

## Purpose
Implements CAIAQ rawmidi support over the EP1 command channel and the preconfigured MIDI output URB.

## Important APIs, Types, and Functions
Public functions are `snd_usb_caiaq_midi_init()`, `snd_usb_caiaq_midi_handle_input()`, and `snd_usb_caiaq_midi_output_done()`. ALSA callbacks include MIDI input/output open/close/trigger and private helper `snd_usb_caiaq_midi_send()`.

## Control Flow
Initialization creates a rawmidi device with port counts from device spec, names it, assigns duplex flags and stream ops when ports exist, and stores the handle. Output trigger records the active output substream and sends immediately if no output URB is active. Send builds an EP1 MIDI_WRITE packet with port zero and length byte, pulls rawmidi bytes into the buffer, submits the pre-initialized `midi_out_urb`, and marks it active. Completion clears active state and sends the next packet if the substream is still active. Input is delivered by `device.c` EP1 reply dispatch and passed to `snd_rawmidi_receive()`.

## State and Persistence
Uses `snd_usb_caiaqdev` fields: `rmidi`, active rawmidi substream pointers, `midi_out_buf`, `midi_out_urb`, and `midi_out_active`.

## Dependencies and Integration Points
Depends on ALSA rawmidi and `device.c` command/URB setup. MIDI input is multiplexed on EP1 with control and input messages.

## Risks
No spinlock protects active substream pointers or `midi_out_active`; trigger, completion, close, and disconnect can race. The `port` argument for input is ignored, and output always uses port 0. Submit failure logs but leaves `midi_out_active` false.

## Test Signals
Test MIDI in/out for devices with different port counts, chained output completions, close while output active, disconnect during URB completion, and multi-port behavior if hardware exposes more than one port.
