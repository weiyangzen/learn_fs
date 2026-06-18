# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-pcm.c

Purpose: provides ALSA PCM-facing operations for generic Intel SOF HDA host DMA streams. It translates ALSA hw_params into HDA stream format fields, allocates a host DMA stream, configures BDL/SPIB policy, exposes pointer and ack callbacks, and releases streams on close.

Important APIs: `hda_dsp_get_mult_div()` and `hda_dsp_get_bits()` encode sample rate and width into SDnFMT bits. `hda_dsp_pcm_open()` selects a free `hdac_ext_stream`, applies runtime constraints, and stores `runtime->private_data`. `hda_dsp_pcm_hw_params()` sets `format_val`, buffer/period sizing, no-period-wakeup, calls `hda_dsp_stream_hw_params()`, configures SPIB depending on `disable_rewinds`, and reports `stream_tag`. `hda_dsp_pcm_trigger()`, `hda_dsp_pcm_pointer()`, `hda_dsp_pcm_ack()`, and `hda_dsp_pcm_close()` bridge ALSA callbacks to the lower stream engine.

Control flow: open finds the SOF PCM by DAI, adjusts pause/rewind/DMI-L1 flags from module parameters and PCM metadata, then calls `hda_dsp_stream_get()`. hw_params programs the stream descriptor and DMA format, while trigger delegates start/stop/pause to `hda_dsp_stream_trigger()`. Pointer prefers firmware IPC positions unless `hda->no_ipc_position` forces direct HDA position reads.

State and persistence: module parameters (`always_enable_dmi_l1`, `disable_rewinds`, `force_pause_support`) affect all streams for the module lifetime. Per-stream state lives in `hdac_stream` fields and the ALSA runtime private pointer.

Dependencies and integration: depends on `hda-stream.c`, SOF PCM objects, ASoC runtime lookup, and HDA format macros. It is exported in `SND_SOC_SOF_INTEL_HDA_COMMON` for platform ops and machine drivers.

Risks and test signals: risks include unsupported sample formats falling back silently, pause capability mismatches, stream leaks if close is skipped, SPIB behavior with rewinds disabled, and pointer source divergence. Test normal playback/capture, dspless S16/S32 constraints, no-period-wakeup, forced pause module parameter, disable-rewinds/appl_ptr ack, and IPC-position versus DPIB-position paths.
