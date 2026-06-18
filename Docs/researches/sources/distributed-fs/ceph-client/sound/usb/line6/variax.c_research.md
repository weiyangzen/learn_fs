# sources/distributed-fs/ceph-client/sound/usb/line6/variax.c

## Purpose
`variax.c` supports Line 6 Variax Workbench and the Variax interface of PODxt Live devices. It is primarily a control/MIDI driver: it performs a staged activation handshake, reacts to initialization sysex messages, and registers the ALSA card once the device is ready.

## Important APIs, Types, And Functions
`struct usb_line6_variax` embeds `struct usb_line6`, stores an allocated activation buffer, and tracks `startup_progress`. Key functions are `variax_probe()`, `variax_init()`, `variax_startup()`, `line6_variax_process_message()`, `variax_activate_async()`, and `line6_variax_disconnect()`.

## Control Flow And State
`variax_init()` installs message, disconnect, and startup callbacks, duplicates the static activation sysex payload, and schedules delayed startup. The startup state machine starts in `VARIAX_STARTUP_VERSIONREQ`, repeatedly schedules itself, and sends async firmware version requests until the expected version sysex is received. `line6_variax_process_message()` recognizes reset messages, the Variax init-version sysex, and the init-done sysex. Version reception advances to `VARIAX_STARTUP_ACTIVATE`; startup then sends the activation sysex with byte 7 set to one and advances to setup. Setup registers the ALSA card.

## State And Persistence
State is volatile and limited to startup progress plus the activation message buffer. The device state changes when activation is sent, but the driver does not persist settings. The activation buffer is freed through the Line 6 disconnect hook.

## Dependencies And Integration Points
The file depends on the common Line 6 driver for USB probe/disconnect/PM, raw async message sending, version requests, and control MIDI capability setup. Device properties describe control endpoints and no standalone audio channel for the Workbench model.

## Risks And Edge Cases
The version request loops until a matching sysex arrives, so devices that never answer rely on delayed work cancellation during disconnect. Message matching uses fixed byte arrays and assumes the common layer supplies complete messages. `snd_card_register()` return value in setup is ignored. Activation buffer allocation failure prevents initialization cleanly.

## Test Signals
Tests should cover startup transitions on init-version and init-done messages, repeated version request scheduling, activation payload mutation, disconnect freeing while delayed work may be pending, reset logging, PODxt Live interface-number matching, and control-only Variax behavior without PCM setup.
