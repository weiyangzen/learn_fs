# sources/distributed-fs/ceph-client/sound/soc/intel/avs/pcm.c

Purpose: Implements the ASoC PCM/component layer for AVS. It registers CPU DAIs for FE, HDA, DMIC, and I2S paths; maps ALSA DPCM callbacks to AVS path operations; configures HDA host/link streams; loads topology and libraries; and replays stream setup across suspend/resume.

Important APIs/functions: DAI callbacks include FE/non-HDA/HDA startup, shutdown, hw_params, hw_free, prepare, trigger, plus `avs_period_elapsed()`. Component callbacks include probe/remove/suspend/resume/open/pointer/mmap/pcm_new. Registration functions are `avs_register_component()`, `avs_register_dmic_component()`, `avs_register_i2s_component()`, and `avs_register_hda_component()`.

Control flow: Startup finds a path template through DAPM graph edges, allocates `avs_dma_data`, applies constraints, and assigns host or link streams. `hw_params` creates an `avs_path`, with FE paths also binding FE-to-BE. Prepare programs HDA stream format and resets/pauses the path. Triggers start/stop HDA streams and run/pause/reset AVS paths. Suspend frees FE paths first, then BE paths; resume recreates BE paths first, then FE paths, then prepares link before host.

State and persistence: `struct avs_dma_data` is stored as DAI DMA data per substream and carries template, live path, stream pointer, constraints, link, substream, and period work. Component probe creates `avs_tplg`, loads firmware topology, loads libraries, refreshes module info, and links the component into `adev->comp_list`.

Dependencies and integration: Integrates ALSA ASoC, HDA extended streams, topology parsing, path lifecycle, firmware/library loading, debugfs topology name, runtime PM, and platform attributes.

Risks: FE/BE ordering is critical; misordering can leak or double-bind paths. L1SEN toggling for single capture stream is hardware-sensitive. The local source snapshot contains duplicated/corrupted blocks and malformed-looking duplicated arguments/braces around prepare, topology debugfs/library code, buffer allocation, and DAI templates; a kernel build is the first required signal. Resume depends on saved position registers and may mark substreams disconnected on failure.

Test signals: Kernel build, DPCM playback/capture, HDA codec PCM enumeration, fallback topology loading, suspend/resume with active FE/BE streams, ignore_suspend low-power paths, pointer/DPIB behavior, XRUN prepare replay, and memory/error unwinding on topology/library load failures.
