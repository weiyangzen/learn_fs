# sources/distributed-fs/ceph-client/sound/usb/midi2.c

## Purpose
`midi2.c` implements USB MIDI 2.0 support for ALSA USB-audio. It detects MIDI 2.0 alternate settings, creates UMP rawmidi endpoints, pairs USB input/output endpoints using group terminal block IDs, parses group terminal block descriptors, starts input UMP traffic, optionally probes UMP endpoint/function-block information, attaches legacy rawmidi views, and falls back to MIDI 1.0 when MIDI 2.0 is disabled or unavailable.

## Important APIs, Types, And Functions
Public functions are `snd_usb_midi_v2_create()`, `snd_usb_midi_v2_suspend_all()`, `snd_usb_midi_v2_resume_all()`, `snd_usb_midi_v2_disconnect_all()`, and `snd_usb_midi_v2_free_all()`. Module parameters are `midi2_enable` and `midi2_ump_probe`.

Core private types are `struct snd_usb_midi2_interface`, `struct snd_usb_midi2_endpoint`, `struct snd_usb_midi2_ump`, and `struct snd_usb_midi2_urb`. UMP callbacks are `snd_usb_midi_v2_open()`, `snd_usb_midi_v2_close()`, `snd_usb_midi_v2_trigger()`, and `snd_usb_midi_v2_drain()`.

## Control Flow And State
`snd_usb_midi_v2_create()` first checks module options, quirk type, alternate-setting count, MIDI 2.0 class header, and endpoint presence. If any condition fails, it calls `__snd_usbmidi_create()` for legacy MIDI 1.0. Otherwise it allocates a MIDI 2.0 interface object, switches to altsetting 1, parses MIDI 2.0 endpoint descriptors, pairs input and output endpoints that share group terminal block IDs, creates unidirectional UMP endpoints for remaining groups, fetches and parses GTB descriptors, allocates and submits input URBs, optionally runs `snd_ump_parse_endpoint()`, creates UMP blocks from GTB fallback data, fills endpoint names/product IDs, and optionally attaches legacy rawmidi devices.

Input endpoints allocate eight URBs at interface creation and keep them running. Completion aligns actual length to 32-bit UMP words, converts little-endian words to CPU order, calls `snd_ump_receive()`, marks the URB free, and resubmits. Output URBs are allocated on UMP open, filled from `snd_ump_transmit()`, converted to little-endian, and submitted while the endpoint running flag is set. Drain waits for all URBs to return or disconnect.

Suspend kills URBs while saving running state; resume restores altsetting, restores running state, and resubmits input or active output. Disconnect marks interface and endpoints disconnected, kills URBs, and drains queues. Free removes endpoint/UMP lists and GTB descriptor storage.

## State And Persistence
All state is runtime: endpoint lists, UMP rawmidi list, GTB descriptor copy, URB free bitmaps, running/suspended atomics, pair links, parsed UMP flags, and `chip->num_rawmidis`. The only module-level state is configuration parameters.

## Dependencies And Integration Points
This file depends on ALSA UMP core, optional legacy UMP rawmidi support, USB MIDI 2.0 descriptor definitions, USB-audio card lists, and the legacy MIDI 1.0 helper for fallback. It uses control transfers to fetch `USB_DT_CS_GR_TRM_BLOCK` descriptors and USB altsetting management for MIDI 2.0 operation.

## Risks And Edge Cases
The code assumes MIDI 2.0 is on altsetting 1. Descriptor parsing must reject malformed endpoint and GTB lengths. Pairing by GTB ID can create only one UMP per ID; devices with unusual block mappings may fall back to unidirectional objects. Input URBs are started during creation before user open, so disconnect/suspend ordering is critical. Output close kills and frees URBs, while input URBs persist until interface free. Errors after adding the interface to `chip->midi_v2_list` rely on `snd_usb_midi_v2_free()` cleanup.

## Test Signals
Test fallback matrix for disabled MIDI2, quirks, missing altsetting, non-MIDI2 headers, and no endpoints. Test descriptor parsing, GTB fetch errors, endpoint pairing/unidirectional creation, UMP open/trigger/drain/close, endian conversion, input always-on delivery, UMP probe fallback to GTB blocks, legacy rawmidi attachment, suspend/resume altsetting restore, disconnect with active URBs, and malformed descriptor length handling.
