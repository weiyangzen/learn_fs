# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda.h

Purpose: central public/private contract header for Intel SOF HDA support. It defines register offsets, bit masks, timeout constants, stream/data structures, helper conversions, exported function prototypes, SoundWire/codec stubs, platform descriptor externs, and DAI widget DMA operation hooks shared by the Intel HDA SOF files.

Important APIs/types: `struct sof_intel_dsp_bdl` describes BDL entries. `struct sof_intel_hda_dev` is the main HDA-private state embedded behind `sdev->pdata->hw_pdata`. `struct sof_intel_hda_stream` wraps `hdac_ext_stream` with SOF device pointer, host reservation, flags, and IOC completion. Inline helpers `sof_to_bus()`, `sof_to_hbus()`, `hstream_to_sof_hda_stream()`, and `bus_to_sof_hda()` define object relationships. `struct hda_dai_widget_dma_ops` abstracts DAI-specific DMA assignment, trigger, codec stream, format, and link operations.

Control flow role: this file does not execute logic, but it shapes control flow by declaring every HDA platform operation used by PCI descriptors, common ops, PCM/stream/probe/trace modules, code loaders, IPC handlers, power management, SoundWire support, codec/i915 integration, and machine selection.

State and persistence: state definitions include DMA buffers retained for firmware load, IMR boot flags, D0i3 work, SDW context, NHLT pointer, mic privacy work, delayed IPC message, and stream completions. Constants define module-wide behavior such as stream limits, BDL size, position quirks, and D0i3 delay.

Dependencies and integration: imports Linux completion/SoundWire/HDA/compress headers and SOF internals. Conditional inline stubs let the same code compile when HDA codec, HDMI/i915, probes, or SoundWire support is disabled.

Risks and test signals: risks include stale register definitions, mismatched prototypes across platform files, conditional stub behavior hiding missing feature coverage, stream/container assumptions, and ABI-like expectations from exported namespaces. Test signals are build coverage across config matrices, sparse/compile warnings, all platform PCI modules, and runtime validation of register offsets on multiple hardware generations.
