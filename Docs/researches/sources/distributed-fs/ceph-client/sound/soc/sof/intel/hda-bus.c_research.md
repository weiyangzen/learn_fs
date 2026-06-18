# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-bus.c

Purpose: `hda-bus.c` initializes and exits the SOF-owned HDA bus abstraction, with conditional support for HDA link and legacy HDA codec drivers. It bridges SOF device state to the ALSA HD-audio core.

Important APIs and types: `sof_hda_bus_init(struct snd_sof_dev *sdev, struct device *dev)` and `sof_hda_bus_exit(struct snd_sof_dev *sdev)` are exported. When HDA audio codec support is enabled, `bus_core_ops` supplies command, response, and link-power callbacks, and `sof_hda_bus_link_power()` customizes codec link power handling. `update_codec_wake_enable()` manages WAKEEN bits according to link power state.

Control flow: init selects one of three paths. With HDA link and codec support, it calls `snd_hdac_ext_bus_init()` with SOF-specific bus core ops and codec extension ops, and enables PIO command mode for ACE 2.0+ hardware. With HDA link but no codec support, it initializes an extended bus without codec ops. Without HDA link support, it manually initializes a minimal `hdac_bus` with device, stream list, IRQ sentinel, index, and register lock.

State and persistence behavior: bus init mutates `struct hdac_bus` inside SOF HDA private state, including stream lists, codec power tracking, command mode, and link power callbacks. Link power changes can release display-power references for iDisp and update WAKEEN for disabled codecs.

Dependencies and integration: it depends on ALSA HDA core, HDA codec, i915 display-power helpers, and `hda.h` SOF conversion helpers. It is called by common HDA probe/remove code outside this work item.

Risks and test signals: link-power state and WAKEEN programming are subtle, especially for display codec power reference symmetry. Minimal-bus mode must still satisfy stream code when HDA link support is compiled out. Test signals include codec command response success, no display power leaks on HDMI codec runtime suspend, codec wake from disabled links, and clean `snd_hdac_ext_bus_exit()` on remove.
