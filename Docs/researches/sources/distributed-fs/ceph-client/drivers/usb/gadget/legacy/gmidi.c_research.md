# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/gmidi.c

## Purpose

`gmidi.c` implements the legacy `g_midi` composite gadget. It exposes a single USB MIDI function backed by ALSA raw MIDI support.

## Important APIs, Types, and Functions

Key functions are `midi_bind()`, `midi_bind_config()`, and `midi_unbind()`. The driver obtains a `"midi"` function instance, fills `struct f_midi_opts` with module parameters (`index`, `id`, `buflen`, `qlen`, `in_ports`, `out_ports`), assigns string IDs, adds one configuration, and releases function resources on unbind.

## Control Flow

Bind obtains the MIDI function instance, copies module parameter values into options, assigns manufacturer/product/configuration string IDs, adds `midi_config`, and applies composite overwrite options. The config callback obtains the concrete MIDI function and adds it. Unbind releases the function and function instance.

## State and Persistence Behavior

State is module parameters plus global function pointers. ALSA card, rawmidi endpoints, queues, and USB request state are owned by the lower-level MIDI function. No state is persisted by this file.

## Dependencies and Integration Points

It depends on libcomposite, ALSA init defaults, USB MIDI function options in `u_midi.h`, dynamic string IDs, and composite options. Host integration is through USB Audio/MIDI class descriptors created by the MIDI function.

## Risks and Test Signals

Risks include invalid queue/buffer/port parameter combinations, cleanup after config-add failure, and host compatibility tied to descriptor strings and vendor/product IDs. Tests should enumerate as a MIDI device, verify ALSA rawmidi ports match parameter counts, exercise IN and OUT MIDI traffic, vary queue/buffer lengths, and unload after active I/O.
