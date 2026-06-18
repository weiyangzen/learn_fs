# sources/distributed-fs/ceph-client/sound/usb/quirks.h

## Purpose

`quirks.h` declares the USB audio quirk interface used across the ALSA USB audio driver. It exposes probe-time quirk creation, boot quirks, format quirks, endpoint/control-message hooks, DSD format augmentation, audioformat attribute repair, and quirk flag parsing/helpers.

## Important APIs

- `snd_usb_create_quirk()` creates streams, MIDI devices, mixers, ignored interfaces, or composite child quirks from a `struct snd_usb_audio_quirk`.
- `snd_usb_apply_interface_quirk()` tells descriptor parsing whether to skip a specific interface alternate setting.
- `snd_usb_apply_boot_quirk()` and `snd_usb_apply_boot_quirk_once()` run early device initialization sequences.
- `snd_usb_set_format_quirk()` performs device-specific work after format selection.
- `snd_usb_is_big_endian_format()` reports special big-endian sample layouts.
- `snd_usb_endpoint_start_quirk()` adjusts endpoint runtime state at start.
- `snd_usb_ctl_msg_quirk()` applies post-control-message delays.
- `snd_usb_select_mode_quirk()` handles mode selection such as native DSD.
- `snd_usb_interface_dsd_format_quirks()` extends supported PCM format masks for DSD devices.
- `snd_usb_audioformat_attributes_quirk()` repairs parsed endpoint attributes.
- `snd_usb_apply_flag_dbg()`, `snd_usb_init_quirk_flags_table()`, `snd_usb_init_quirk_flags_parse_string()`, `snd_usb_quirk_flag_find_name()`, and `snd_usb_quirk_flags_from_name()` manage behavior quirk flags.

## Control Flow And State

The header carries no implementation or persistent state. It forms the compile-time contract between core probe code, descriptor parsing, PCM setup, endpoint logic, and the quirk implementation in `quirks.c`. Runtime state flows through `struct snd_usb_audio`, `struct audioformat`, `struct snd_usb_endpoint`, and `struct snd_usb_substream`.

## Dependencies And Integration Points

The declarations depend on forward declarations for `audioformat`, `snd_usb_endpoint`, and `snd_usb_substream`, plus the full `struct snd_usb_audio` and `struct snd_usb_audio_quirk` definitions visible to includers through `usbaudio.h`. The header is used by `stream.c`, `quirks.c`, and other USB audio modules that need hook points without including quirk internals.

## Risks

- Signature changes affect several driver modules and must stay synchronized with the implementation.
- New quirk flags need API coverage here only if external modules need to initialize, parse, or inspect them.
- Forward declarations keep compile coupling low but require includers to include the proper definitions before dereferencing types.

## Test Signals

- A full driver build catches declaration/definition mismatches.
- Probe tests verify that call sites can link against the exported quirk implementation.
