# sources/distributed-fs/ceph-client/include/sound/hda_codec.h

Source read summary: 580 lines, legacy HD-audio codec interface layered on top of the generic `hdac_device`/`hdac_bus` core.

Purpose: defines the legacy ALSA HDA codec bus, codec driver, PCM, pin, SPDIF, GPIO, power-management, patch-loader, and DSP-loader contracts used by `sound/pci/hda` codec parsers and controller glue.

Important APIs, types, and functions: `struct hda_bus` extends `struct hdac_bus` with card, PCI, PCM-device bitmap, reset/probe/power flags, and mixer assignment state. `struct hda_codec_driver`, `struct hda_codec_ops`, `struct hda_pcm_ops`, `struct hda_pcm_stream`, `struct hda_pcm`, and `struct hda_codec` define driver callbacks, PCM stream descriptors, codec-private state, parser caches, connection lists, pin overrides, SPDIF state, jack polling, fixups, init verbs, and power accounting. Constructors and lifecycle calls include `snd_hda_codec_device_init()`, `snd_hda_codec_new()`, `snd_hda_codec_configure()`, register/unregister, and unbind cleanup. Verb helpers wrap core `snd_hdac_codec_read/write`, regmap cached writes, connection-list queries, device-select verbs, pin configuration, SPDIF assignment, PCM creation, stream setup/cleanup, GPIO, power-save, and optional patch/DSP loading.

Control flow: controller code creates an `hda_bus`, probes codec addresses, instantiates `hda_codec`, matches `hda_codec_driver` IDs, runs codec `probe`, `build_controls`, `build_pcms`, and `init`, then exposes ALSA controls/PCMs. PCM open/prepare delegates to `hda_pcm_ops`, programs stream tags and formats on converter NIDs, and cleanup tears down stream state. Runtime events arrive as unsolicited responses or jack-poll work; reset paths coordinate bus/device locks and codec reconfiguration.

State and persistence behavior: codec state is in-kernel and card-lifetime only: widget caps, pin/default overrides, connection overrides, mixer arrays, SPDIF controls, PCM refcounts, jack tables, power-on/off accounting, fixup identity, and optional user reconfiguration arrays. Hardware state persists only in codec registers until reset/suspend; this header defines caches and replay inputs for restoration.

Dependencies and integration points: depends on ALSA control/PCM/hwdep/info, generic HD-audio core, HDA verb definitions, regmap, PCI, module device IDs, runtime PM, and optional `CONFIG_SND_HDA_RECONFIG`, `CONFIG_SND_HDA_HWDEP`, patch loader, and DSP loader. It bridges codec parser modules, controller drivers, proc/hwdep diagnostics, jack reporting, and PCM stream handling.

Risks and edge cases: risks include codec lifetime races around `pcm_ref` and unbind, stale cached verbs after reset, connection-list overrides diverging from hardware topology, inconsistent pin power/shutup behavior, jack polling during suspend, and optional config stubs hiding missing DSP/patch support. Duplicated declarations/macros in this source snapshot should be treated as merge drift signals.

Test signals: validate codec probe/unbind, generic and vendor parser selection, jack unsolicited and polling paths, pin override via hwdep/reconfig, SPDIF reassignment, PCM prepare/cleanup across suspend/resume, bus reset fallback behavior, power-save accounting, and compile matrices with HDA hwdep/reconfig/DSP/patch options enabled and disabled.
