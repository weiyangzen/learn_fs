# sources/distributed-fs/ceph-client/sound/usb/quirks.c

## Purpose

`quirks.c` implements the ALSA USB audio driver's non-standard device handling. It converts quirk table entries into audio streams, MIDI interfaces, mixers, endpoint setup, boot-time USB control sequences, format-switch commands, DSD format augmentation, endpoint-start workarounds, and per-device behavior flags.

The file is the bridge between static VID/PID quirks and runtime driver state in `struct snd_usb_audio`, `struct audioformat`, `struct snd_usb_substream`, and `struct snd_usb_endpoint`.

## Important APIs And Functions

- `snd_usb_create_quirk()` dispatches a `struct snd_usb_audio_quirk` by `quirk->type`.
- `create_composite_quirk()` recursively handles per-interface child quirks and claims otherwise-unused interfaces.
- `create_standard_audio_quirk()` calls `snd_usb_parse_audio_interface()` for standard audio interfaces.
- `create_fixed_stream_quirk()` duplicates a fixed `audioformat`, validates interface/altsetting/endpoint indexes, registers streams and endpoints, and initializes pitch/sample rate.
- `create_any_midi_quirk()`, `create_auto_midi_quirk()`, `create_yamaha_midi_quirk()`, `create_roland_midi_quirk()`, and `create_std_midi_quirk()` create MIDI or autodetected MIDI interfaces.
- `create_uaxx_quirk()` handles Edirol UA-series PCM/MIDI modes using endpoint count and packet size to infer the sample rate.
- `snd_usb_apply_boot_quirk()` and `snd_usb_apply_boot_quirk_once()` run VID/PID-specific USB control or reset sequences.
- `snd_usb_apply_interface_quirk()` filters alternate settings for M-Audio and PreSonus devices using `chip->setup`.
- `snd_usb_is_big_endian_format()` marks specific M-Audio formats as big-endian.
- `snd_usb_set_format_quirk()` performs per-format setup for E-Mu, MacroSilicon, Pioneer DJM, Mbox 3, and RME Digiface devices.
- `snd_usb_select_mode_quirk()` switches ITF-USB DSD DACs between PCM and native DSD modes.
- `snd_usb_endpoint_start_quirk()` adjusts initial feedback/data packet handling.
- `snd_usb_ctl_msg_quirk()` adds post-control-message delays based on quirk flags.
- `snd_usb_interface_dsd_format_quirks()` adds native DSD or DoP format bits for known DACs.
- `snd_usb_audioformat_attributes_quirk()` repairs class-specific endpoint attributes.
- `snd_usb_init_quirk_flags_table()` initializes `chip->quirk_flags` from built-in VID/PID or string matches.
- `snd_usb_init_quirk_flags_parse_string()` applies module-parameter flag overrides by VID/PID and flag name or hex mask.

## Control Flow

Probe-time quirk creation starts with `snd_usb_create_quirk()`. For composite quirks, each child interface is looked up by number, skipped if missing or already claimed by another probe path, and dispatched recursively. After successful child setup, unclaimed child interfaces are claimed with `USB_AUDIO_IFACE_UNUSED` to keep other drivers from binding to pieces of the same audio function.

Fixed audio quirks allocate a private `audioformat` copy, optionally duplicate the rate table, validate table-provided indexes against actual descriptors, fill missing runtime fields such as protocol, data interval, max packet size, and format type, then call `snd_usb_add_audio_stream()` and `snd_usb_add_endpoint()`. Standard quirks delegate descriptor parsing to `stream.c`.

Boot quirks run before normal interface creation for devices that need reconfiguration, firmware wake-up, mode switching, or register initialization. Some return `-ENODEV` or `-EAGAIN` intentionally to abort the current enumeration because the device will reconnect or reconfigure.

After stream creation, format and endpoint hooks run later in the PCM lifecycle. They may set hardware sample rates, add stream offsets, switch mode for DSD, ignore bogus initial feedback packets, or delay control-message pacing.

## State And Persistence Behavior

Primary persistent state is in `chip->quirk_flags`, `chip->setup`, stream lists, endpoint lists, and per-format fields. `snd_usb_init_quirk_flags_table()` ORs matching built-in flags into `chip->quirk_flags` and stops at the first match. `snd_usb_init_quirk_flags_parse_string()` can mask or unmask flags from a module parameter for matching devices.

Fixed stream setup allocates `audioformat` instances and possibly copied rate tables that become owned by the PCM stream list and are freed by `stream.c`. Boot quirks usually do not persist state in memory, but they may permanently change the USB device's current configuration, internal registers, clock source, mixer defaults, or descriptor mode until unplug/reset.

## Dependencies And Integration Points

This file depends on the USB core, ALSA core/PCM/control APIs, class-specific USB audio descriptors, and driver-local helpers from `card.h`, `mixer.h`, `mixer_quirks.h`, `midi.h`, `midi2.h`, `helper.h`, `endpoint.h`, `pcm.h`, `clock.h`, and `stream.h`.

Important integration points include:

- `quirks-table.h` and `usbaudio.h` define the quirk types and data shapes this file consumes.
- `stream.c` provides `snd_usb_parse_audio_interface()` and `snd_usb_add_audio_stream()`.
- Endpoint code consumes `snd_usb_endpoint_start_quirk()` and endpoint type decisions.
- Format and clock code call DSD, sample-rate, and format-selection quirks.
- Mixer code uses behavior flags such as min-mute and linear-volume flags.

## Risks

- Many USB control sequences are empirical and device-specific; changing request/value/index pairs can brick the probe path for a model.
- Returning the wrong error from a boot quirk can either continue with an unusable pre-boot interface or abort a valid device.
- Fixed stream allocation must keep ownership clear. A failed path unlinks and frees `audioformat`; a successful path hands it to stream teardown.
- Built-in flag table matching stops at the first match, so order is significant, especially device-specific exceptions before vendor-wide entries.
- Module parameter parsing applies after matching VID/PID fields and supports unmasking; malformed flag strings may silently stop parsing later entries.
- `snd_usb_apply_flag_dbg()` indexes flag names by set bits; new flags must update both `usbaudio.h` and the name table.

## Test Signals

- Compile with `CONFIG_SND_USB_AUDIO` to catch quirk function table, enum, and type drift.
- Probe devices affected by boot quirks and verify expected reconnect, configuration, or initialization messages.
- Use `/proc/asound/card*/stream*`, ALSA PCM open tests, MIDI enumeration, and sample-rate switching to verify stream creation.
- Exercise module parameter `quirk_flags` with names, hex masks, and `!` unmasking.
- Test DSD-capable DACs with PCM, DoP, and native DSD formats where available.
- Run suspend/resume and stream restart tests for endpoint-start and interface-reset flags.
