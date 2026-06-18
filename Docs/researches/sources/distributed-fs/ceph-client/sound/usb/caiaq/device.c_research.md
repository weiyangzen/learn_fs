# sources/distributed-fs/ceph-client/sound/usb/caiaq/device.c

## Purpose
Owns CAIAQ USB driver probe/disconnect, EP1 command transport, device spec discovery, product-specific startup, ALSA card creation, and subsystem initialization.

## Important APIs, Types, and Functions
USB lifecycle functions are `snd_probe()` and `snd_disconnect()`. Card helpers include `create_card()`, `init_card()`, `setup_card()`, and `card_free()`. EP1 command functions are `snd_usb_caiaq_send_command()`, `snd_usb_caiaq_send_command_bank()`, `snd_usb_caiaq_set_audio_params()`, and `snd_usb_caiaq_set_auto_msg()`. Completion handler `usb_ep1_command_reply_dispatch()` routes device info, audio-param acknowledgments, MIDI input, control-state reads, and input events.

## Control Flow
Probe creates an ALSA card with embedded `snd_usb_caiaqdev`, stores intfdata, sets interface 0 altsetting 1, initializes EP1 input and MIDI output bulk URBs, submits EP1 input, requests device info, waits for spec, gets USB strings, names the card, and calls `setup_card()`. Setup performs product-specific startup writes, initializes audio if any audio I/O exists, initializes MIDI if MIDI ports exist, optionally initializes input, registers the card, then adds controls. Disconnect disconnects ALSA, tears down input/audio, kills EP1 and MIDI output URBs, and defers card free.

## State and Persistence
State is centralized in `snd_usb_caiaqdev`, embedding a generic `snd_usb_audio` plus EP buffers, spec, wait queues, flags, product strings, audio/MIDI/control/input state, and ALSA handles. USB device refcount is held via `usb_get_dev()` until `card_free()`.

## Dependencies and Integration Points
Depends on USB core, ALSA core/PCM/rawmidi/control, and local `audio.c`, `midi.c`, `control.c`, and optional `input.c`. Uses Native Instruments USB ids declared in `device.h`.

## Risks
`enable[]` selection in `create_card()` picks the first enabled slot rather than tracking occupied slots, unlike many ALSA drivers; multiple devices may compete for the same configured slot behavior. `snd_usb_caiaq_send_command()` does not validate `actual_len` for bulk sends. EP1 command replies requeue after processing but return without requeue on URB error. Controls are added after card registration, which can expose a partially initialized card if control init fails.

## Test Signals
Test every product id path, device-info timeout, audio-param ack timeout/failure, EP1 MIDI/input dispatch, Audio 8 DJ control-state initialization, disconnect during waits, and probe with multiple CAIAQ devices.
