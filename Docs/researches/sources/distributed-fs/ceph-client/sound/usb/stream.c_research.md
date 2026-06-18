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
