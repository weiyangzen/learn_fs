# sources/distributed-fs/ceph-client/sound/hda/common/hda_local.h

## Purpose
Provides the central private/public helper interface for common HD-audio codec code. It collects mixer-control macros, amp and pin helpers, fixup/quirk types, SPDIF and multi-output helpers, proc/hwdep/sysfs hooks, power helpers, HDMI ELD helpers, enum/input-mux helpers, and logging macros.

## Important APIs, Types, And Functions
Key definitions include `HDA_CODEC_VOLUME*`, `HDA_CODEC_MUTE*`, amp private-value encoders/decoders, `struct hda_vmaster_mute_hook`, `struct hda_input_mux`, `struct hda_multi_out`, `struct hda_pintbl`, `struct hda_fixup`, `struct hda_quirk`, `struct snd_hda_pin_quirk`, `struct hda_nid_item`, `struct hda_amp_list`, `struct hda_loopback_check`, and `struct hdmi_eld`. It declares most helpers implemented by `codec.c`, proc/hwdep/sysfs modules, and HDMI ELD code.

## Control Flow
Codec patch drivers include this header to construct controls, apply fixups, parse pins, manipulate amps and pins, create SPDIF/multi-output PCMs, implement power checks, and register proc/hwdep interfaces. Macros encode HDA node/channel/direction/index information into ALSA control `private_value` fields consumed by callbacks in `codec.c`.

## State And Persistence Behavior
The header does not own state directly, but defines the shapes and encodings for codec-owned arrays, control metadata, fixup tables, loopback power state, and HDMI ELD buffers. Its macros determine how mixer controls map back to HDA hardware registers.

## Dependencies And Integration Points
Depends on ALSA PCM DRM ELD definitions, HDA codec/register APIs, procfs, hwdep, sysfs, and runtime PM helpers. It is included by most common HDA files and many codec-specific patch drivers.

## Risks And Test Signals
Risks include ABI-like macro encoding changes, mismatched private-value decoding, quirk/fixup ordering mistakes, maximum input/output array limits, and conditional stubs hiding missing feature support. Test signals include successful build across configuration combinations, mixer TLV correctness, fixup application on known hardware IDs, pin-control safety, SPDIF/multi-output routing, proc/hwdep presence, and power loopback behavior.
