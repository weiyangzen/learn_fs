# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/hdmi_local.h

## Purpose

This private header defines the shared HDMI codec data model and exported helper APIs used by generic HDMI, simple HDMI, Intel, NVIDIA, and Tegra codec drivers.

## Important APIs, types, and functions

`struct hdmi_spec_per_cvt` tracks converter NID, assignment, silent-stream ownership, and PCM capability limits. `struct hdmi_spec_per_pin` tracks virtual pin identity, MST device id, mux list, attached PCM, ELD, delayed work, channel-map override, setup state, and non-PCM status. `struct hdmi_ops` is the vendor override table for ELD reads, infoframe programming, HBR setup, stream setup, pin/converter fixups, and silent-stream control. `struct hdmi_spec` is the codec-wide state container. The header also defines HDMI and DP audio infoframe layouts, supported PCM capability macros, array access macros, and prototypes for generic/simple HDMI helpers.

## Control flow

The header has no runtime flow, but it defines the callback boundaries that `hdmi.c` calls during parse, open, prepare, hotplug, and component binding. Vendor modules populate selected `hdmi_ops` entries after `snd_hda_hdmi_generic_alloc`.

## State and persistence behavior

All state described here is runtime codec state attached to `codec->spec`. It persists for the lifetime of the bound HDA codec driver and is freed by generic or simple remove paths.

## Dependencies and integration points

It includes ALSA core, jack, HDA codec, HDA i915, and HDA channel-map headers, plus local HDA helpers. It is the ABI within the HDMI codec module namespace, with symbols exported under `SND_HDA_CODEC_HDMI`.

## Risks and test signals

Risks are layout and contract drift between generic and vendor files, especially around `pcm_rec[8]`, MST `dev_num`, `port_map`, and optional `CONFIG_SND_HDA_COMPONENT` behavior. Build coverage across all HDMI codec modules and runtime tests on generic, Intel, NVIDIA, and Tegra devices are the main signals.
