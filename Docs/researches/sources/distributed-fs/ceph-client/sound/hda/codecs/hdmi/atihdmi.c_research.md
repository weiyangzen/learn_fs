# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/atihdmi.c

## Purpose
Implements the AMD/ATI HDMI and DisplayPort HD-audio codec driver. It layers AMD-specific verbs, ELD emulation, channel mapping, HBR control, ramp-rate setup, and GPU audio-component binding on top of the generic HDMI codec implementation.

## Important APIs, Types, and Functions
The driver defines AMD vendor verbs for channel allocation, downmix info, multichannel slot mapping, HBR control, ramp rate, and sink/ELD emulation. `get_eld_ati()` synthesizes a baseline ELD buffer from AMD-specific speaker allocation, sink info, audio descriptor, and latency verbs. `atihdmi_pin_get_eld()`, `atihdmi_pin_setup_infoframe()`, `atihdmi_pin_hbr_setup()`, and `atihdmi_setup_stream()` are installed into `hdmi_spec.ops`. Channel-map overrides include `atihdmi_pin_set_slot_channel()`, `atihdmi_pin_get_slot_channel()`, `atihdmi_paired_chmap_validate()`, `atihdmi_paired_chmap_cea_alloc_validate_get_type()`, and `atihdmi_paired_cea_alloc_to_tlv_chmap()`.

The module registers `atihdmi_codec_ops`, an HDA ID table for RS600/RS690/R6xx HDMI devices, and `atihdmi_driver` via `module_hda_codec_driver()`. It imports the `SND_HDA_CODEC_HDMI` namespace.

## Control Flow
Probe first calls `snd_hda_hdmi_generic_probe()` and then customizes the returned `struct hdmi_spec`: static PCM mapping is enabled, AMD-specific pin/stream ops are installed, and channel-map ops are overridden. Pre-rev3 AMD codecs use pairwise channel remapping with FC/LFE swap handling; rev3-or-later codecs support full per-channel remap and single-channel mode. Probe also expands converter capability fields because AMD converters do not advertise all rates, formats, channel counts, or bit depths, enables link-down-at-suspend, and binds to the DRM audio component with AMD pin-to-port mapping.

Init delegates to `snd_hda_hdmi_generic_init()`, clears downmix info on every pin, enables single-channel multichannel mode on full-remap hardware, and enables auto runtime PM. Stream setup writes an AMD ramp-rate verb on rev3+ hardware, disabling ramp for non-PCM formats, then calls generic HDMI stream setup. Runtime callbacks for ELD, infoframe channel allocation, HBR, and slot mapping issue AMD vendor verbs against the pin or converter NIDs.

## State and Persistence Behavior
Persistent device state lives in `codec->spec` as the generic `hdmi_spec` plus AMD-installed ops and modified converter capabilities. Hardware state includes pin downmix info, multichannel mode, slot-channel mapping, HBR enable state, channel allocation, and converter ramp rate. `get_eld_ati()` writes sink-info/audio-descriptor indices before reading associated data but stores the synthesized ELD only in the caller-provided buffer.

## Dependencies and Integration Points
The file depends on Linux module/init/slab/unaligned helpers, ALSA core/TLV/HDA APIs, `hda_local.h`, and `hdmi_local.h`. It integrates with generic HDMI helpers for probe/remove/init/build PCMs/build controls/unsolicited events/suspend/resume and with DRM audio-component callbacks for pin ELD notifications and master bind/unbind. The Kconfig option selects generic HDMI support and the Makefile builds this as `snd-hda-codec-atihdmi`.

## Risks
Pre-rev3 pairwise remapping is fragile: odd/even slots, silent companion channels, and FC/LFE swapping must agree between validation, TLV generation, set, and get paths. `get_eld_ati()` synthesizes standardized ELD from vendor registers, so incorrect SAD count, sink-name length truncation, alignment, or latency conversion can make user space see wrong sink capabilities. The driver assumes AMD pin NIDs map to ports as `pin / 2 - 1` and reverse as `port * 2 + 3`; new hardware layouts could violate that convention. Forcing converter capabilities may advertise functionality the hardware or sink path cannot actually use if assumptions become stale.

## Test Signals
Signals include successful probe/init on listed AMD IDs, valid `/proc/asound` or control ELD data for HDMI and DP sinks, correct PCM capability exposure up to 8 channels/24 bit/supported rates, working HBR passthrough for capable pins and rejection on incapable pins, channel-map validation for pre-rev3 pairwise maps, proper FC/LFE behavior, no audio gaps or artifacts around non-PCM ramp-rate handling, DRM audio-component ELD notifications mapping to the expected port, and suspend/resume keeping link and pin state coherent.
