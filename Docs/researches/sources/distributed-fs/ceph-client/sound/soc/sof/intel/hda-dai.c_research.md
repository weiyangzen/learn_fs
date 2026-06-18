# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-dai.c

Purpose: `hda-dai.c` implements ASoC DAI callbacks and DAI driver registration for SOF HDA platforms. It bridges topology widgets, HDA link DMA streams, IPC DAI configuration, SoundWire channel mapping, and platform DAI driver ops.

Important APIs: exported functions include `hda_dai_config()`, `sdw_hda_dai_hw_params()`, `sdw_hda_dai_hw_free()`, `sdw_hda_dai_trigger()`, `hda_set_dai_drv_ops()`, `hda_ops_free()`, `hda_dsp_dais_suspend()`, and the exported `skl_dai[]` DAI array. Internal callbacks cover HDA link DMA hw_params, cleanup, trigger, hw_free, prepare, non-HDA DAI setup, and suspend cleanup.

Control flow: `hda_dai_get_ops()` locates the DAPM widget for the CPU DAI and stream, obtains SOF widget/DAI private data, selects widget DMA ops via `hda_select_dai_widget_ops()`, validates mandatory ops, and caches them. HW params assigns or reuses a link stream, maps playback stream IDs to HDA links, configures codec DAI stream pointers, resets and formats the stream, marks it prepared, then calls topology DAI config with the stream tag. IPC4 non-HDA setup additionally fills copier DMA config TLVs with HDA DMA method and stream IDs. SoundWire setup resets and programs PCMSyCM channel maps and propagates TLVs across aggregated DAIs.

State and persistence behavior: state persists in DAI DMA data, `sdai->platform_private`, `hext_stream->link_prepared`, `host_reserved`, `sof_ipc4_copier` DMA config TLVs, SoundWire channel maps, `ipc4_data->nhlt`, and `sdev->private`. `hda_ops_free()` releases NHLT and IPC4 private data.

Dependencies and integration: it depends on ASoC DAPM/DPCM, Intel NHLT parsing, HDA multi-link helpers, IPC3/IPC4 topology ops, and the operation tables from `hda-dai-ops.c`.

Risks and test signals: null widgets and mismatched machine/topology DAI links are explicitly guarded. Risks include unbalanced link DMA cleanup on pause/suspend, incorrect SoundWire channel masks for aggregated devices, and forgetting to free NHLT/private IPC4 data. Test signals include prepare/hw_params idempotence, suspend during pause, IPC3 HW_FREE/PAUSE DAI config messages, IPC4 copier TLVs, SoundWire restart after xrun, and DAI names/channels from `skl_dai[]`.
