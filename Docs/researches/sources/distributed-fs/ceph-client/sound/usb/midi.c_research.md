# sources/distributed-fs/ceph-client/sound/usb/midi.c

## Purpose
`midi.c` is the legacy ALSA USB MIDI 1.0 helper driver. It discovers MIDIStreaming endpoints or applies quirk metadata, creates ALSA rawmidi ports, translates between ALSA byte streams and USB MIDI event packets, handles many vendor-specific protocols, manages input/output URBs, and provides suspend/resume/disconnect helpers for USB-audio users.

## Important APIs, Types, And Functions
The exported entry point is `__snd_usbmidi_create()`, wrapped by `snd_usbmidi_create()` in `midi.h`. Exported lifecycle helpers are `snd_usbmidi_disconnect()`, `snd_usbmidi_input_stop()`, `snd_usbmidi_input_start()`, `snd_usbmidi_suspend()`, and `snd_usbmidi_resume()`.

Core types are `struct snd_usb_midi`, `struct snd_usb_midi_out_endpoint`, `struct snd_usb_midi_in_endpoint`, `struct usbmidi_out_port`, and `struct usb_protocol_ops`. Protocol operations cover standard USB MIDI, Midiman, broken M-Audio running status, CME, CH345 broken sysex, Akai, Novation, raw bytes, FTDI, Tascam US-122L, and Emagic.

## Control Flow And State
`__snd_usbmidi_create()` allocates `snd_usb_midi`, initializes locks/timer, selects protocol operations and endpoint detection based on quirk type, counts input/output cables, creates an ALSA rawmidi device, creates endpoints/ports, takes an autosuspend reference, and links the instance into the caller's MIDI list.

Input endpoints allocate seven URBs and coherent buffers. Completion calls the selected protocol parser, which eventually calls `snd_usbmidi_input_data()` for a cable/port if the ALSA input substream is triggered, then resubmits the URB. Recoverable USB errors defer resubmission via `error_timer`.

Output endpoints allocate seven URBs and coherent buffers. ALSA output trigger marks a port active and queues high-priority work. `snd_usbmidi_do_output()` picks free URBs round-robin, asks the protocol formatter to fill the transfer buffer from rawmidi substreams, submits non-empty URBs, and tracks active bits. Completion clears active/drain bits, wakes drain waiters, and refills output. Standard output uses a MIDI byte state machine to assemble CIN packets, including sysex states and running channel messages.

Rawmidi open/close updates `opened[]`, starts input when an input stream opens, stops it when all input streams close, and handles Roland alternate-setting control in a mutex. Disconnect sets `disconnected` under rwsem/spinlock, shuts down the error timer, cancels work, kills all URBs, runs protocol finish hooks, clears buffers, wakes drains, and frees input endpoints.

## State And Persistence
State is entirely runtime: endpoint objects, URB bitmaps, rawmidi substream bindings, protocol parser state (`running_status_length`, `in_sysex`, `seen_f5`, current port), open counts, trigger bits, Roland load control value, and disconnect/input-running flags. No settings are persisted by the driver.

## Dependencies And Integration Points
The file integrates USB core bulk/interrupt transfers, ALSA rawmidi and sequencer port metadata, USB-audio quirk definitions, autosuspend power management, helper descriptor accessors, and optional vendor controls. It is used by generic USB-audio and by specialized drivers such as UA-101.

## Risks And Edge Cases
The risk surface is broad: malformed descriptors, devices with incorrect endpoint packet sizes, quirk-specific packet formats, URB completion races with disconnect/timer/work, drain waits, and alternate-setting changes while ports are open. Some endpoint detection paths trust quirk-provided cable masks. The standard output state machine must not overrun `max_transfer`; vendor parsers must handle short packets and malformed sysex. Cleanup frees input endpoints during disconnect and later frees output endpoint containers during rawmidi free, so ordering is important.

## Test Signals
Test standard MIDI event packet encode/decode, sysex fragmentation, realtime interleaving, every quirk protocol parser/formatter, descriptor discovery for standard/Yamaha/Roland/Midiman paths, rawmidi open/close/trigger/drain behavior, input stop/start around suspend and Roland altsetting changes, disconnect races with active URBs and error timer, low-speed interrupt fallback, fixed packet-size device exceptions, and port naming/sequence flags.
