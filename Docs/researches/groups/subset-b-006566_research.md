# Research: subset-b-006566

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/quirks-table.h -->
# sources/distributed-fs/ceph-client/sound/usb/quirks-table.h

## Purpose

`quirks-table.h` is the device-ID and descriptor override table included by the ALSA USB audio driver ID table. It exists for USB audio/MIDI hardware whose descriptors are missing, misleading, vendor-specific, or whose alternate-interface layout needs forced handling. The file is intentionally data-heavy: each table entry matches a USB device/interface and optionally attaches a `struct snd_usb_audio_quirk` through `QUIRK_DRIVER_INFO`.

The table is part of probe-time device selection. It does not execute logic directly, but it selects quirk types and inline data consumed by `quirks.c`, `midi.c`, `stream.c`, mixer setup, and endpoint setup.

## Important APIs, Types, And Macros

- `USB_DEVICE_VENDOR_SPEC(vend, prod)` matches a vendor/product only when the interface class is vendor-specific. It prevents quirk handling from applying to unrelated standard interfaces on the same device.
- `USB_AUDIO_DEVICE(vend, prod)` matches USB audio control interfaces by VID/PID and audio class/subclass.
- `QUIRK_DRIVER_INFO` stores a pointer to a compound-literal `struct snd_usb_audio_quirk` in `.driver_info`.
- `QUIRK_DATA_IGNORE`, `QUIRK_DATA_STANDARD_AUDIO`, `QUIRK_DATA_STANDARD_MIDI`, and `QUIRK_DATA_STANDARD_MIXER` encode simple interface actions.
- `QUIRK_DATA_COMPOSITE` creates an array of child `struct snd_usb_audio_quirk` entries terminated by `QUIRK_COMPOSITE_END`.
- `QUIRK_DATA_AUDIOFORMAT` embeds a fixed `struct audioformat`, including endpoint address, format bitmask, channel count, alternate setting, rate table, sync endpoint, implicit feedback flag, and clock ID.
- `QUIRK_DATA_MIDI_FIXED_ENDPOINT`, `QUIRK_DATA_MIDI_MIDIMAN`, and `QUIRK_DATA_MIDI_EMAGIC` embed `struct snd_usb_midi_endpoint_info`.
- Local generator macros such as `YAMAHA_DEVICE`, `YAMAHA_INTERFACE`, `QUIRK_RME_DIGIFACE`, and `QUIRK_AF16RIG` reduce repeated entries for large related device families.

## Control Flow And Data Shape

The file is written as a sequence of initializer entries for a surrounding `struct usb_device_id` array. During USB probing, the kernel USB core matches an entry, and the driver retrieves `.driver_info` as a quirk descriptor. `snd_usb_create_quirk()` then dispatches by `quirk->type`.

Composite entries are the dominant pattern. They describe per-interface actions in order, for example: ignore a broken control or HID-like interface, parse a standard mixer, create fixed playback/capture audio formats, and then create MIDI endpoints. Fixed audio entries are used where the device descriptor cannot be trusted and the driver must provide the ALSA-visible PCM format contract itself.

The table covers broad families: Creative, Yamaha, Roland/Edirol/BOSS, M-Audio/Midiman, MOTU, Emagic, KORG, AKAI, Steinberg, TerraTec, Novation/Focusrite, Native Instruments, Digidesign, TASCAM, Denon, Pioneer/AlphaTheta DJ devices, MacroSilicon capture devices, Fiero, RME Digiface, Arturia AF16Rig, and catch-all MIDI streaming or vendor-specific autodetect matches.

## State And Persistence Behavior

The file contains static, compile-time data only. There is no runtime persistence, locking, allocation, or cleanup here. Runtime state arises after consumers copy or interpret the data. Fixed `rate_table` arrays are compound literals referenced through the quirk data and copied by `create_fixed_stream_quirk()` when needed, which makes the table's lifetime appropriate for static driver data while still allowing mutable per-device `audioformat` instances at probe time.

## Dependencies And Integration Points

This table depends on USB matching macros and ALSA USB audio structures from the surrounding driver includes. It must stay consistent with:

- `enum quirk_type` and `struct snd_usb_audio_quirk` in `usbaudio.h`.
- `snd_usb_create_quirk()` dispatch in `quirks.c`.
- MIDI endpoint quirk handling in the USB MIDI code.
- `struct audioformat` fields consumed by `stream.c`, endpoint setup, format parsing, and PCM setup.
- Boot and flag quirks in `quirks.c`, because some devices have both ID-table quirks and separate VID/PID-specific boot or behavior flags.

## Risks

- A wrong endpoint address, `ep_idx`, `altset_idx`, `sync_ep`, or implicit feedback flag can create silent audio, channel swaps, feedback failures, or probe errors.
- Broad matches such as vendor-specific catch-alls can claim devices that would otherwise work through standard descriptors; ordering and match flags matter.
- `QUIRK_NODEV_INTERFACE` entries intentionally block generic handling for devices owned by another driver; misusing them can make a device disappear.
- Some fixed-format entries encode rates and packet sizes discovered empirically; adding rates without hardware validation can create broken ALSA formats.
- Compound macro definitions obscure initializer boundaries, so syntax errors or missing terminators can affect many entries.

## Test Signals

- Build-test the USB audio driver after edits; initializer syntax and enum/type mismatches are caught at compile time.
- Probe affected devices and inspect `dmesg`, ALSA card creation, PCM device list, MIDI device list, and `/proc/asound/card*/stream*`.
- Exercise playback/capture at every advertised rate/channel count for fixed audio entries.
- For implicit-feedback entries, test simultaneous playback/capture and xrun recovery.
- For broad match changes, test unrelated devices sharing the same vendor ID to catch accidental claiming.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/quirks-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/quirks.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/quirks.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/stream.c -->
# sources/distributed-fs/ceph-client/sound/usb/stream.c

## Purpose

`stream.c` parses USB Audio Class streaming interfaces and turns descriptors or fixed quirk formats into ALSA PCM streams. It owns `audioformat` lifetime within stream format lists, creates PCM devices and substreams, builds channel-map controls, registers endpoints, initializes sample rate/pitch, and supports UAC1, UAC2, UAC3, and UAC3 BADD profiles.

## Important APIs And Functions

- `snd_usb_parse_audio_interface()` is the public parser for one interface number. It parses PCM formats first and non-PCM formats in a second pass if needed.
- `snd_usb_add_audio_stream()` adds a parsed or fixed `audioformat` to an existing endpoint-compatible substream or creates a new ALSA PCM device/substream.
- `audioformat_free()`, `free_substream()`, `snd_usb_audio_stream_free()`, and `snd_usb_audio_pcm_free()` implement stream and format cleanup.
- `snd_usb_init_substream()` initializes `struct snd_usb_substream`, sets transfer quirks from `chip->quirk_flags`, attaches the first format, assigns optional UAC3 power domain state, and preallocates buffers.
- `add_chmap()` and the `usb_chmap_ctl_*()` callbacks expose fixed channel maps to ALSA controls.
- `convert_chmap()` maps UAC1/UAC2 channel config bits to ALSA channel map positions.
- `convert_chmap_v3()` maps UAC3 cluster descriptors to ALSA channel maps.
- `parse_uac_endpoint_attributes()` locates class-specific endpoint descriptors and normalizes UAC1/UAC2/UAC3 attributes.
- `snd_usb_get_audioformat_uac12()` parses UAC1/UAC2 AS_GENERAL and FORMAT_TYPE descriptors, terminal channel data, clocks, endpoint attributes, and audio formats.
- `snd_usb_get_audioformat_uac3()` parses UAC3 BADD or high-capability cluster descriptors, power domains, clocks, and formats.
- `__snd_usb_parse_audio_interface()` iterates alternate settings, filters invalid endpoints, applies quirks, parses formats, adds streams/endpoints, and initializes interfaces.

## Control Flow

`snd_usb_parse_audio_interface()` calls the internal parser for PCM. If a non-PCM format type was seen, it calls the parser again requesting non-PCM formats. This allows type-I PCM and non-PCM formats to be separated when the same interface exposes both.

The internal parser gets the USB interface by number, applies a Dallas DS4201 altsetting limit, and loops through alternate settings. Each altsetting must be audio/vendor class, have an isochronous endpoint with nonzero packet size, and pass `snd_usb_apply_interface_quirk()`. Protocol-specific parsing then creates an `audioformat`.

For UAC1/UAC2, the parser reads AS_GENERAL, terminal descriptors, format type, channel count/config, clock source for UAC2, endpoint attributes, and format/rate data through `snd_usb_parse_audio_format()`. For UAC3, it either derives BADD formats from endpoint packet size or requests a high-capability cluster descriptor over control endpoint zero, then parses UAC3 format data and power domains.

After a valid format is built, the parser sets implicit or explicit sync endpoints, calls `snd_usb_add_audio_stream()`, adds the data endpoint and optional sync endpoint, then performs probe-time interface setup unless `QUIRK_FLAG_SKIP_IFACE_SETUP` is set. UAC1 and `QUIRK_FLAG_SET_IFACE_FIRST` set the alternate interface before pitch/rate initialization; otherwise setup occurs after rate initialization.

## State And Persistence Behavior

`snd_usb_add_audio_stream()` mutates `chip->pcm_list`, `chip->pcm_devs`, and per-PCM `snd_usb_stream` objects. Formats are linked into `subs->fmt_list` and freed when the PCM private data is freed. `chip->need_delayed_register` is set if a new stream is added after the ALSA card is already registered.

Substreams persist fields derived from the first and later formats: format bitmask, format type, endpoint number, maximum channels, speed, transfer quirks, offset adjustments, power-domain pointer, and buffer preallocation. UAC3 power domains can be allocated during parsing and are either assigned to the substream or automatically freed on the loop iteration.

Channel-map controls persist in ALSA control objects and read the current substream format when queried. Endpoint objects are managed by endpoint code after `snd_usb_add_endpoint()`.

## Dependencies And Integration Points

The file integrates with:

- `quirks.c` for interface skipping and audioformat attribute fixes.
- `format.c` through `snd_usb_parse_audio_format()` and `snd_usb_parse_audio_format_v3()`.
- `endpoint.c` for data/sync endpoint registration.
- `pcm.c` for PCM operations and buffer preallocation.
- `clock.c` for pitch and sample-rate initialization.
- `power.c` for UAC3 power domains.
- `media.c` for media-controller stream cleanup.
- ALSA PCM/control/TLV APIs for PCM devices and channel-map controls.

## Risks

- Descriptor parsing is defensive but still depends on accurate length checks; missing checks can become malformed-device memory bugs.
- `convert_chmap()` checks `channels > ARRAY_SIZE(chmap->map)` before allocation using the type expression; maintainers should preserve this idiom carefully.
- Adding formats to an existing substream skips channel-map control creation for new maps after the initial control was added unless the stream creation path accounts for it.
- Format ownership is strict: successful `snd_usb_add_audio_stream()` transfers ownership; error paths must free and unlink.
- Interface setup order is device-sensitive. Changing `set_iface_first`, skip flags, or rate/pitch ordering can regress UAC1 devices and vendor quirks.
- UAC3 high-capability descriptor retrieval occurs via USB control messages at probe time and can fail or block device creation.

## Test Signals

- Build with UAC1/UAC2/UAC3 descriptor support enabled.
- Probe representative UAC1, UAC2, UAC3, BADD, vendor-specific Roland, implicit-feedback, and fixed-quirk devices.
- Inspect `/proc/asound/card*/stream*` for endpoint, format, rate, channel, and sync endpoint correctness.
- Validate ALSA channel-map controls with `amixer` or control API tests.
- Open PCM playback/capture at advertised rates and channel counts, including non-PCM formats when present.
- Exercise suspend/resume, disconnect, and error paths under USB descriptor fuzzing or invalid-device tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/stream.h -->
# sources/distributed-fs/ceph-client/sound/usb/stream.h

## Purpose

`stream.h` declares the public stream construction interface for the ALSA USB audio driver. It lets other modules parse a USB audio streaming interface and add already-constructed `audioformat` objects to ALSA PCM streams.

## Important APIs

- `snd_usb_parse_audio_interface(struct snd_usb_audio *chip, int iface_no)` parses all usable alternate settings on a USB audio streaming interface and registers PCM streams/endpoints.
- `snd_usb_add_audio_stream(struct snd_usb_audio *chip, int stream, struct audioformat *fp, struct snd_usb_power_domain **pdptr)` attaches an `audioformat` to an ALSA PCM stream, creating the PCM device or substream if needed. `pdptr` is optional and is cleared when ownership transfers to the substream.

## Control Flow And State

The header itself has no runtime logic. It exposes functions implemented by `stream.c` and used by quirk creation, standard probe code, and fixed-format handling. State changes occur in the implementation: `chip->pcm_list`, endpoint lists, PCM devices, format lists, and optional power-domain ownership.

## Dependencies And Integration Points

It depends on visible declarations for `struct snd_usb_audio`, `struct audioformat`, and `struct snd_usb_power_domain` from includers. `quirks.c` uses both declarations to create standard and fixed audio paths.

## Risks

- Callers of `snd_usb_add_audio_stream()` must respect ownership: after success, the format is owned by the stream list and must not be freed by the caller.
- The `stream` argument must be an ALSA PCM stream direction matching the endpoint direction, or the stream topology becomes inconsistent.

## Test Signals

- Build/link tests catch signature drift.
- Fixed-format quirk probing validates external callers of `snd_usb_add_audio_stream()`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usbaudio.h -->
# sources/distributed-fs/ceph-client/sound/usb/usbaudio.h

## Purpose

`usbaudio.h` defines core types, constants, helpers, and quirk flag bit assignments shared across the ALSA USB audio driver. It is the central header for `struct snd_usb_audio`, quirk descriptors, USB ID helpers, logging macros, shutdown-lock helpers, and driver behavior flags.

## Important APIs, Types, And Macros

- `USB_ID(vendor, product)`, `USB_ID_VENDOR(id)`, and `USB_ID_PRODUCT(id)` pack and unpack VID/PID pairs.
- `MAX_CARD_INTERFACES` sets the tracked interface capacity per card.
- `struct snd_intf_to_ctrl` maps streaming/MIDI interfaces back to an audio control interface.
- `struct snd_usb_audio` is the main per-card device state: USB device, ALSA card, interfaces, quirk type/flags, mutexes, suspend/shutdown state, PCM/endpoint/mixer/MIDI lists, module parameter values, UAC3 BADD profile, media-controller handles, and control-interface mappings.
- `USB_AUDIO_IFACE_UNUSED` is a sentinel stored as interface driver data when composite quirks claim child interfaces without creating a full ALSA card for them.
- `usb_audio_err/warn/info/dbg` wrap device-scoped logging.
- `QUIRK_NODEV_INTERFACE`, `QUIRK_NO_INTERFACE`, and `QUIRK_ANY_INTERFACE` are special interface selectors.
- `enum quirk_type` enumerates quirk actions consumed by `snd_usb_create_quirk()`.
- `struct snd_usb_audio_quirk` describes a quirk entry: optional names, interface number, type, and type-specific data.
- `combine_word`, `combine_triple`, and `combine_quad` read little-endian descriptor byte sequences.
- `snd_usb_lock_shutdown()`, `snd_usb_unlock_shutdown()`, and the `DEFINE_CLASS(snd_usb_lock, ...)` cleanup helper provide scoped shutdown-safe locking.
- `QUIRK_TYPE_*` enum values and `QUIRK_FLAG_*` macros define bit positions for behavior flags in `chip->quirk_flags`.

## Control Flow And State

`struct snd_usb_audio` persists for the lifetime of an ALSA USB audio card. Probe code fills device/card/interface fields, initializes lists, applies quirk flags, parses interfaces into PCM and MIDI devices, and later uses suspend/shutdown state to coordinate disconnect and runtime operations.

The quirk type enum drives probe-time dispatch. The quirk flag enum drives behavior throughout the driver, including sample-rate reads, media-controller sharing, transfer alignment, implicit feedback selection, clock handling, control-message delay, autosuspend, DSD formats, interface reset/skip behavior, fixed-rate handling, microphone volume resolution, and mixer volume semantics.

## Dependencies And Integration Points

This header is included broadly by USB audio modules. It integrates with Linux USB structures, ALSA card and PCM subsystems, media controller types, list management, atomics, mutexes, wait queues, and driver-local modules for card, mixer, MIDI, endpoint, stream, clock, and power behavior.

The quirk flag names in `quirks.c` must remain aligned with the `QUIRK_TYPE_*` bit positions. The `enum quirk_type` must remain aligned with the dispatch table in `snd_usb_create_quirk()`.

## Risks

- Adding a quirk type without updating the dispatch table can lead to invalid or null function dispatch.
- Adding a quirk flag without updating `snd_usb_audio_quirk_flag_names[]` breaks name-based module parameter parsing and debug names.
- `MAX_CARD_INTERFACES` bounds arrays for interface tracking and control mappings; code that assumes more interfaces risks overflow if not checked elsewhere.
- `quirk_flags` is `unsigned int`, while helper APIs use `u32` or `unsigned long`; bit-count assumptions should remain within 32 behavior flags.
- The scoped lock helper must only be used in code paths where early unlock on nonzero lock error is correct.

## Test Signals

- Full build catches enum/name/signature mismatches.
- Probe tests on multi-interface devices validate interface tracking and sentinel handling.
- Module parameter tests for `quirk_flags` validate bit assignments and name parsing.
- Suspend/disconnect stress tests validate shutdown lock behavior and atomic state transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usbaudio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/Makefile -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/Makefile

## Purpose

This Makefile defines the ALSA USB usx2y-family kernel module objects. It maps Kconfig symbols to composite object targets for the legacy TASCAM US-X2Y, US-122L, and US-144MKII drivers.

## Important Targets

- `snd-usb-usx2y-y := usbusx2y.o usX2Yhwdep.o usx2yhwdeppcm.o` builds the original US-X2Y module.
- `snd-usb-us122l-y := us122l.o` builds the US-122L/US-144/US-122MKII driver module from one source object.
- `snd-usb-us144mkii-y := ...` builds the US-144MKII module from core, PCM, MIDI, playback, capture, and controls objects.
- `obj-$(CONFIG_SND_USB_USX2Y)`, `obj-$(CONFIG_SND_USB_US122L)`, and `obj-$(CONFIG_SND_USB_US144MKII)` include modules conditionally by Kconfig.

## Control Flow And State

There is no runtime control flow or state. The file affects build graph composition only.

## Dependencies And Integration Points

The object lists depend on source files in the same directory and Kconfig symbols defined elsewhere in the ALSA USB build. `us122l.o` includes `usb_stream.c` directly from `us122l.c`, so this Makefile only lists `us122l.o` for that module.

## Risks

- Missing an object in a composite target causes link failures or missing driver functionality.
- Renaming source files without updating this Makefile breaks module builds.
- Because `us122l.c` includes implementation code directly, adding `usb_stream.o` separately here would likely create duplicate definitions.

## Test Signals

- Kernel build with each `CONFIG_SND_USB_*` option enabled as module and built-in.
- Module load tests for `snd-usb-us122l`, `snd-usb-usx2y`, and `snd-usb-us144mkii`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us122l.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us122l.c

## Purpose

`us122l.c` implements a dedicated ALSA USB driver for TASCAM US-122L, US-144, and US-122MKII style devices. Unlike the generic USB audio path, it exposes a hardware-dependent `SNDRV_HWDEP_IFACE_USB_STREAM` interface and uses the `usb_stream` engine for userspace-mapped low-latency audio buffers plus separate USB MIDI creation.

## Important APIs, Functions, And Data

- Module parameters `index`, `id`, and `enable` select ALSA card allocation.
- `US122L_FLAG_US144` marks device IDs that need US-144 handling.
- `snd_us122l_card_used[]` tracks occupied ALSA card slots.
- `us122l_create_usbmidi()` and `us144_create_usbmidi()` create MIDI interfaces using `QUIRK_MIDI_US122L` endpoint data.
- `pt_info_set()` sends vendor-specific control messages used during startup/resume.
- `usb_stream_hwdep_vm_fault()` maps the `usb_stream` read buffer and write page to userspace pages.
- `usb_stream_hwdep_open()` and `usb_stream_hwdep_release()` enforce at most two users and manage USB autosuspend references.
- `usb_stream_hwdep_mmap()` validates read/write mmap regions and installs VM fault operations.
- `usb_stream_hwdep_poll()` reports period progress through `periods_done` and per-file polling cursors.
- `usb_stream_hwdep_ioctl()` implements `SNDRV_USB_STREAM_IOCTL_SET_PARAMS`.
- `us122l_start()`, `us122l_stop()`, and `us122l_set_sample_rate()` manage the streaming engine and endpoint sample rate.
- `usb_stream_hwdep_new()` creates the ALSA hwdep device.
- `us122l_create_card()`, `usx2y_create_card()`, `us122l_usb_probe()`, and `snd_us122l_probe()` allocate, initialize, register, and bind the ALSA card.
- `snd_us122l_disconnect()`, `snd_us122l_suspend()`, and `snd_us122l_resume()` implement lifecycle and power handling.
- `snd_us122l_usb_id_table` matches TASCAM VID `0x0644` products `US122L`, `US144`, and `US122MKII`.

## Control Flow

USB probing ignores interfaces other than interface 1, checks the US-144 high-speed restriction, creates an ALSA card, sets interface alternate setting 1, sends two vendor `pt_info_set()` commands, starts streaming at 44.1 kHz with 256-period frames, creates MIDI, creates the hwdep node, registers the card, and stores it in interface data.

Userspace opens the hwdep device, maps read and write regions, then issues `SNDRV_USB_STREAM_IOCTL_SET_PARAMS`. The ioctl validates ABI version, supported rates, frame size, period size, and speed constraints. The first opener becomes `master`; a second opener can become `slave` only if it uses the same stream config. If config changes or the stream is in xrun, the driver stops and restarts the USB stream and returns `1` to indicate a restart.

Polling uses `usb_stream` period counters. The first opener compares against `s->periods_polled`; the second compares against `us122l->second_periods_polled`. The mmap fault handler maps either the shared read area or the write page after checking offsets.

Disconnect stops the stream under the device mutex, disconnects MIDI resources, and frees the card when closed. Suspend stops MIDI input and streaming; resume restores alternate settings, sends vendor setup commands, restores the previous sample rate, restarts streaming, and restarts MIDI input.

## State And Persistence Behavior

`struct us122l` is stored in `card->private_data` and persists with the ALSA card. It holds the USB device, card index, `usb_stream_kernel` state, mutex, first/master/slave file pointers, second poll cursor, MIDI list, and US-144 flag.

`snd_us122l_card_used[]` persists module-wide and is cleared in `snd_us122l_free()`. Open file pointers determine master/slave streaming ownership until release. `usb_stream_kernel` owns the live streaming buffer state and waitqueue. Device sample rate and interface altsettings are restored on resume from `us122l->sk.s->cfg.sample_rate`.

## Dependencies And Integration Points

The driver depends on Linux USB, ALSA core/hwdep/PCM/initval APIs, USB audio descriptors, the shared USB MIDI implementation, `../usbaudio.h`, local `us122l.h`, and directly included `usb_stream.c`. It registers as its own `struct usb_driver`, separate from the generic `snd-usb-audio` path.

Userspace integration is through ALSA hwdep with `SNDRV_USB_STREAM_IOCTL_SET_PARAMS`, mmap, and poll. MIDI integration uses `snd_usbmidi_create()` and stops/starts MIDI input alongside stream state.

## Risks

- Directly including `usb_stream.c` is unusual and can create duplicate definitions if the build graph changes.
- `usb_stream_hwdep_mmap()` dereferences `us122l->sk.s` after locking without a null check; callers are expected to mmap only after stream setup.
- Resume assumes `us122l->sk.s` is available when restoring sample rate; failed or stopped stream state could make this fragile.
- Master/slave file tracking is simple and relies on hwdep `used` count plus mutex-protected release updates.
- Vendor control messages ignore the return value in `pt_info_set()`, so failed setup can surface later as stream failure.
- US-144 is rejected at high speed with a user-facing message; test environments using EHCI/xHCI may never bind that model.

## Test Signals

- Build with `CONFIG_SND_USB_US122L`.
- Probe each matched product ID and confirm only interface 1 binds for card creation.
- Open hwdep from one and two processes, verify master/slave config rules and `-EIO` on mismatched second config.
- mmap read/write regions and verify page faults, poll wakeups, and period counters under streaming.
- Test valid rates: 44.1/48 kHz generally, plus 88.2/96 kHz only on high-speed-capable hardware.
- Exercise disconnect, suspend/resume, xrun restart, and MIDI input restart.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us122l.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us122l.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us122l.h

## Purpose

`us122l.h` defines the private state and device constants for the TASCAM US-122L family driver implemented in `us122l.c`.

## Important Types And Macros

- `struct us122l` stores the driver-private card state: `usb_device`, ALSA card slot index, optional stride, `usb_stream_kernel`, mutex, first/master/slave file pointers, second poll cursor, MIDI list, and `is_us144` flag.
- `US122L(c)` casts an ALSA card's `private_data` to `struct us122l *`.
- `NAME_ALLCAPS` provides the common product name text used in module metadata and card strings.
- `USB_ID_US122L`, `USB_ID_US144`, `USB_ID_US122MKII`, and `USB_ID_US144MKII` define TASCAM product IDs.

## Control Flow And State

The header contains no executable logic. `struct us122l` is allocated as the private area of an ALSA card by `snd_card_new()` in `us122l.c`, initialized during probe, and used by hwdep, MIDI, streaming, suspend/resume, and disconnect paths.

## Dependencies And Integration Points

The structure depends on `struct usb_device`, `struct usb_stream_kernel`, kernel mutex/file/list types, and the ALSA card private data convention. It is tightly coupled to `us122l.c`; the product ID constants also align with the USB device ID table there.

## Risks

- Changing `struct us122l` layout affects all hwdep and lifecycle code because fields are accessed directly.
- `USB_ID_US144MKII` is defined here but not matched by `us122l.c`; that device is built by the separate US-144MKII module.
- The `stride` field is present but unused in `us122l.c`, so changes should verify whether other included code expects it.

## Test Signals

- Build-test `snd-usb-us122l` after structure or constant changes.
- Probe matched devices and exercise hwdep open/ioctl/mmap/poll paths to validate private state initialization.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us122l.h -->
