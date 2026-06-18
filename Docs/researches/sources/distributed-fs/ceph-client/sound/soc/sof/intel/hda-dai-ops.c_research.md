# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-dai-ops.c

Purpose: `hda-dai-ops.c` defines the per-widget DMA operation tables selected by `hda-dai.c` for HDA, SSP, DMIC, SoundWire/ALH, IPC3, IPC4, chain DMA, and dspless paths. It is the low-level link-DMA policy layer.

Important APIs and structures: the exported API is `hda_select_dai_widget_ops()`. Internal helpers assign and release `hdac_ext_stream` objects, calculate stream formats, map HDA links, set codec streams, manage IPC4 pipeline trigger ordering, and implement dspless stream lookups. Operation tables include `hda_ipc4_dma_ops`, `ssp_ipc4_dma_ops`, `dmic_ipc4_dma_ops`, `sdw_ipc4_dma_ops`, `hda_ipc4_chain_dma_ops`, `sdw_ipc4_chain_dma_ops`, `hda_ipc3_dma_ops`, `hda_dspless_dma_ops`, and `sdw_dspless_dma_ops`.

Control flow: stream assignment scans the HDA bus stream list under `bus->reg_lock`, chooses a compatible unlocked link stream, handles PROCEN format quirks by matching FE stream tags when needed, reserves host DMA for hostless streams, decouples host/link DMA, and records `link_substream`. IPC4 pre-trigger pauses pipelines before stop/suspend/pause, the trigger starts or clears the HDAC ext stream, and post-trigger transitions pipelines to running or updates `started_count`. Format calculators adapt HDA codec significant bits, generic physical width, and DMIC S16-as-S32 packing.

State and persistence behavior: operation selection is cached in `sdai->platform_private`. Stream state persists in DAI DMA data, `hext_stream->link_locked`, `link_prepared`, `link_substream`, saved LLP registers, and pipeline state. Dspless mode bypasses firmware pipeline state and uses host stream state.

Dependencies, risks, and test signals: the file depends on ASoC DPCM, HDAC extended streams, HDA multi-link helpers, IPC4 pipeline state APIs, and SOF topology private data. Risks include stream leaks, wrong stream-tag mapping, invalid pipeline state transitions, and null topology widgets. Test HDA codec playback/capture, SSP and DMIC on ACE 2.0+, SoundWire aggregated channel mapping, pause/resume delay accounting, chain DMA, dspless mode, and xrun restart paths.
