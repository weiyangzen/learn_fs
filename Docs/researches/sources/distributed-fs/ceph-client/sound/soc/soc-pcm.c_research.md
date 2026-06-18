# sources/distributed-fs/ceph-client/sound/soc/soc-pcm.c

## Purpose
This is the core ASoC PCM orchestration file. It creates ALSA PCM devices for DAI links, computes hardware constraints across CPU and codec DAIs, sequences component/link/DAI callbacks, manages DAPM stream events, and implements Dynamic PCM (DPCM) frontend/backend routing, state transitions, runtime updates, and debugfs state reporting.

## Important APIs, Types, and Functions
Externally visible functions include `snd_soc_runtime_action()`, `snd_soc_runtime_ignore_pmdown_time()`, `snd_soc_runtime_calc_hw()`, `snd_soc_dpcm_get_substream()`, `snd_soc_dpcm_runtime_update()`, `dpcm_be_dai_trigger()`, `widget_in_list()`, and `dpcm_end_walk_at_be()`. Internally, the non-DPCM PCM operation path is `soc_pcm_open()`, `soc_pcm_hw_params()`, `soc_pcm_prepare()`, `soc_pcm_trigger()`, `soc_pcm_hw_free()`, `soc_pcm_close()`, and `soc_pcm_pointer()`. DPCM uses `dpcm_fe_dai_open()`, `dpcm_fe_dai_hw_params()`, `dpcm_fe_dai_prepare()`, `dpcm_fe_dai_trigger()`, `dpcm_fe_dai_hw_free()`, and `dpcm_fe_dai_close()`.

Key state lives in `struct snd_soc_pcm_runtime`, `struct snd_soc_dpcm`, per-stream DPCM state (`state`, `runtime_update`, `trigger_pending`, `users`, `be_start`, `be_pause`, `fe_pause`, `hw_params`), and ALSA `struct snd_pcm_substream`.

## Control Flow
`soc_new_pcm()` determines playback/capture support, creates an ALSA PCM, installs either regular PCM ops or DPCM frontend ops, and attaches component callbacks like copy, mmap, ack, ioctl, and sync_stop. Regular open selects default pinctrl state, runtime-PM gets components, opens components/link/DAIs, computes compatible hardware from all participating DAIs, applies MSB and symmetry constraints, and activates runtime state. Hw_params applies symmetry, calls link, codec DAIs, CPU DAIs, and components, with TDM channel-mask fixups. Prepare starts DAPM and unmutes DAIs. Trigger selects link/component/DAI ordering from component or link policy and performs rollback on start failure. Close and hw_free reverse the setup and restore power state.

DPCM open discovers backend paths through DAPM, connects FE and BE `struct snd_soc_dpcm` links, opens BEs, opens the FE, and merges FE/BE hardware constraints as configured. DPCM runtime updates first prune old paths, then add new paths, starting or stopping BEs according to FE state. BE operations are guarded by state checks so shared BEs are not reconfigured while other FEs are running. Trigger code tracks shared BE start and pause reference counts and honors FE trigger ordering (`PRE` or `POST`).

## State and Persistence
Runtime state is protected by the ASoC DPCM mutex and, for trigger races, ALSA stream locks. DPCM connections persist in FE `be_clients` and BE `fe_clients` lists until pruned and disconnected. Debugfs exposes FE and BE DPCM state and hardware params for dynamic links. DAI symmetry parameters persist on DAIs while active and are cleared when inactive.

## Dependencies and Integration Points
This file integrates ALSA PCM core, ASoC components, DAIs, DAI links, DAPM, pinctrl, runtime PM, debugfs, and `soc-link.c`. It is also the central consumer of topology-created DAI links and dynamic routes.

## Risks and Test Signals
Main risks are DPCM shared-BE user count underflow/overflow, racey trigger_pending behavior, rollback asymmetry, invalid dynamic multi-CPU configurations, DAPM route changes while streams are active, and mismatched hardware constraints across CPU/codec DAIs. Test signals include normal PCM playback/capture, DPCM FE open with no backend route, route switching while active, shared BE with two FEs, pause-to-stop transitions, trigger rollback injection, suspend/resume, debugfs state inspection, and TDM channel-map cases.
