# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-codec.c

Purpose: `hda-codec.c` handles legacy HD-audio codec discovery, module binding, command I/O lifecycle, jack wake/check behavior, RIRB status handling, and i915 display audio power integration for SOF HDA platforms.

Important APIs: exported functions include `hda_codec_probe_bus()`, `hda_codec_detect_mask()`, `hda_codec_jack_wake_enable()`, `hda_codec_jack_check()`, command I/O init/resume/stop/suspend helpers, RIRB helpers, wakeup control, device removal, and optional i915 init/exit/display-power helpers. The module parameter `codec_mask` filters probed codec slots.

Control flow: `hda_codec_detect_mask()` reads `STATESTS` if no codec mask exists and applies the module filter. `hda_codec_probe_bus()` walks up to `HDA_MAX_CODECS`, probing each masked address. `hda_codec_probe()` sends a vendor-ID verb with retries, allocates `hdac_hda_priv`, creates an HDA codec device, marks display codecs as needing i915 audio power, chooses generic probing when requested, registers the device, and requests or attaches the codec module. Failure unregisters and drops the codec device.

State and persistence behavior: runtime state includes `bus->codec_mask`, `codec_powered`, command DMA state, WAKEEN/STATESTS/RIRBSTS hardware bits, codec private data, and i915 audio component references. Jack wake enable programs WAKEEN only for codecs with jack tables when enabling, and clears HD-audio codec WAKEEN when disabling.

Dependencies and integration: this file is compiled only with HDA audio codec support and optionally HDMI codec support. It relies on ALSA HDA codec core, module autoloading, SOF no-codec debug flags, and i915 HDA component helpers.

Risks and test signals: codec probing crosses firmware, BIOS, and module-autoload boundaries. Risks include leaked device references on attach failures, display power imbalance, RIRB interrupt races, and no-codec debug bypass divergence. Test signals include codec mask filtering, generic codec fallback, HDMI/iDisp probe with and without i915 component, jack wake from suspend, RIRB response processing, and clean codec removal.
