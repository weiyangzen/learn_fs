# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_cfg.c

## Purpose
Parses XenStore sound-card configuration into ALSA hardware constraints, PCM instances, and stream descriptors for the Xen sound frontend.

## Important APIs, Types, And Functions
- `CFG_HW_SUPPORTED_RATES` and `CFG_HW_SUPPORTED_FORMATS` map XenStore string tokens to ALSA rate/format masks.
- `SND_DRV_PCM_HW_DEFAULT` provides fallback PCM constraints.
- `cfg_read_pcm_hw()` inherits parent constraints and applies XenStore overrides for channels, sample rates, sample formats, and buffer size.
- `cfg_get_stream_type()` counts playback versus capture streams.
- `cfg_stream()` fills a stream descriptor, assigns the global stream index, stores its XenStore path, and reads stream-level constraints.
- `cfg_device()` parses one PCM device node and allocates playback/capture stream arrays.
- `xen_snd_front_cfg_card()` parses the whole card under the XenBus node and returns total stream count.

## Control Flow
Card parsing counts numeric device nodes under the frontend XenBus path. It reads default card hardware, allocates `pcm_instances`, then parses each device. Device parsing reads optional name and hardware overrides, counts numeric stream nodes up to `VSND_MAX_STREAM`, allocates playback/capture stream arrays, and fills each stream. Constraint inheritance flows card -> device -> stream.

## State And Persistence
Parsed state is stored in `front_info->cfg` using devm-managed arrays tied to the XenBus device. XenStore is the persistent source of truth; kernel state is rebuilt on backend init/reinit.

## Dependencies And Integration Points
Depends on XenBus reads/existence checks, Xen sound interface string constants, ALSA `snd_pcm_hardware`, and the ALSA creation code in `xen_snd_front_alsa.c`.

## Risks
- Unknown sample-rate or format strings are silently ignored; if all are unknown, inherited/default constraints remain.
- `rate_min` initializes to unsigned `-1`, relying on wrap to pick the first valid rate.
- `period_bytes_max` is forced to `buffer_bytes_max` and `periods_max` depends on `period_bytes_min`; invalid small/zero values would be dangerous, though defaults avoid zero.
- Numeric device/stream enumeration stops at the first missing node.

## Test Signals
Use XenStore configs with multiple devices, mixed playback/capture streams, per-card/device/stream overrides, missing stream type, invalid type, invalid format/rate strings, no devices, and maximum stream counts. Verify resulting ALSA PCM constraints.
