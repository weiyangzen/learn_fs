<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.c

## Purpose
Main USB driver for older TASCAM US-X2Y devices (US-122, US-224, US-428). It creates the initial ALSA card and hwdep loader, manages interrupt/bulk pipe 4 control traffic, and handles hotplug cleanup.

## APIs, Types, and Functions
Registers `snd_usx2y_usb_driver`. Exports `usx2y_async_seq04_init()` and `usx2y_in04_init()`. Important internals are `snd_usx2y_probe()`, `snd_usx2y_disconnect()`, `usx2y_create_card()`, `snd_usx2y_card_private_free()`, `i_usx2y_in04_int()`, `i_usx2y_out04_int()`, and `usx2y_unlinkseq()`.

## Control Flow, State, and Persistence
Probe validates vendor/product IDs, creates a card with `struct usx2ydev` private data, initializes wait queues, mutex, MIDI list, and card strings, then creates the hwdep loader and registers the card. The real audio/MIDI device stack is created later after firmware load. Pipe-4 input interrupt completions detect changed 21-byte control snapshots, publish them to `us428ctls_sharedmem`, wake pollers, submit queued async output URBs for sample-rate/control sequences or light/volume requests, and resubmit the IN interrupt URB. Disconnect marks hangup, kills async/control URBs, disconnects MIDI children, wakes pollers, and frees when closed.

## Dependencies and Integration
Depends on USB core, ALSA card/rawmidi, `usX2Yhwdep.c` firmware loader, `usbusx2yaudio.c`, and shared control definitions.

## Risks and Test Signals
Risks include staged initialization complexity, pipe-4 output loss noted by FIXME, `dev_set_drvdata()` versus `usb_get_intfdata()` expectations, firmware timing, and hot-unplug while hwdep mmap is active. Test signals are probe for all three product IDs, firmware load, interrupt-control snapshots, p4out light/volume commands, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.c -->
