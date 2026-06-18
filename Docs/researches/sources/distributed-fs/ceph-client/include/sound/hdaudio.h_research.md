# sources/distributed-fs/ceph-client/include/sound/hdaudio.h

Source read summary: 765 lines, generic HD-audio core bus/device/stream interface.

Purpose: defines the reusable HD-audio core below legacy and ASoC HDA drivers: codec devices, bus command transport, CORB/RIRB bookkeeping, controller MMIO helpers, stream DMA descriptors, runtime PM helpers, widget arrays, DSP loader hooks, and PCI controller matching helpers.

Important APIs, types, and functions: `hda_nid_t`, `struct snd_array`, `struct hdac_device`, `struct hdac_driver`, `struct hdac_bus_ops`, `struct hdac_ext_bus_ops`, `struct hdac_rb`, `struct hdac_bus`, and `struct hdac_stream` are central. APIs cover device init/register, chip names/modalias, widget refresh, verb reads/writes, parameter overrides, connection parsing, PCM format generation, power up/down, driver matching, bus init/exit, command I/O, chip reset, stream IRQ handling, stream page allocation, stream assign/release/setup/start/stop/reset/sync, SPIB/DRSM/DPIB/LPIB operations, DSP prepare/trigger/cleanup, widget capability helpers, `snd_array` helpers, and GPU/controller PCI predicates.

Control flow: controller probe initializes `hdac_bus`, parses capabilities, resets the link, initializes command DMA, discovers codecs into `codec_list`, and registers `hdac_device` instances. Stream users assign an idle `hdac_stream`, set up BDL/format/periods, start DMA, handle IRQ status through bus callbacks, and release on close. Codec code sends verbs through `hdac_bus_ops` or device `exec_verb`; PM helpers wrap runtime power transitions.

State and persistence behavior: bus state includes MMIO base, IRQ, capability pointers, codec address table, unsolicited event ring/work, codec power mask, CORB/RIRB buffers and pending responses, stream list, DMA buffers, feature flags, locks, DRM display-power state, link list, and address offset. Stream state tracks BDL/position buffers, substreams, format tags, running/prepared flags, timestamps, and optional DSP lock. All state is device-lifetime and hardware-restored after reset/suspend.

Dependencies and integration points: depends on Linux device/PCI/PM/io/timecounter, ALSA core/PCM/memalloc, HDA verbs/registers, and DRM i915 component declarations. It underpins legacy HDA, ASoC HDA, HDMI/DP audio, DSP loading, and controller-specific drivers.

Risks and edge cases: command DMA vs PIO fallback, RIRB response timeouts, unsolicited ring wrap, aligned-MMIO platform differences, duplicate fields visible in this snapshot, stream tag reuse, DMA buffer alignment, and runtime PM during verb access are high-risk areas.

Test signals: codec discovery, CORB/RIRB and immediate-command paths, stream playback/capture DMA, interrupt and polling modes, runtime PM, display power integration, DSP loader paths, aligned MMIO builds, and multi-controller PCI matching.
