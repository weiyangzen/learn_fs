# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-pcm.c

## Purpose
IPC4 PCM runtime operations for SOF. It controls pipeline state transitions for PCM triggers, handles special ChainDMA streams, performs DAI link hardware-parameter fixups, allocates per-stream pipeline/time state, and computes PCM pointer plus delay from host counters and firmware register windows.

## APIs, Types, and Functions
The exported ops object is `ipc4_pcm_ops`; `sof_ipc4_set_pipeline_state()` is exported for direct pipeline state changes. Important helpers include `sof_ipc4_set_multi_pipeline_state()`, trigger-list ordering helpers, `sof_ipc4_chain_dma_trigger()`, `sof_ipc4_trigger_pipelines()`, DAI fixup helpers, `sof_ipc4_pcm_setup/free()`, `sof_ipc4_build_time_info()`, `sof_ipc4_pcm_hw_params()`, `sof_ipc4_get_stream_start_offset()`, `sof_ipc4_pcm_pointer()`, and `sof_ipc4_pcm_delay()`. Local state lives in `sof_ipc4_pcm_stream_priv` and `sof_ipc4_timestamp_info`.

## Control Flow, State, and Persistence
PCM trigger commands map to IPC4 RUNNING or PAUSED; `hw_free` maps to RESET. For normal pipelines, the code builds a priority-sorted trigger list while holding `pipeline_state_mutex`, sends an intermediate PAUSED transition when required, then sends final RUNNING/PAUSED/RESET via single-pipeline or multi-pipeline IPC. It updates `started_count`, `paused_count`, and each `sof_ipc4_pipeline.state` only for pipelines actually triggered. ChainDMA bypasses module pipeline triggering and constructs a global ChainDMA IPC from host/link DMA ids, allocation/enable bits, SCS, and fifo size; stream-private `chain_dma_allocated` prevents duplicate reset. PCM setup allocates per-direction pipeline lists sized by firmware `max_num_pipelines` and enables playback delay reporting only when firmware register ABI and host byte-counter callbacks are available.

## Dependencies and Integration
Depends on ASoC PCM callbacks, SOF IPC send paths, topology-created pipeline lists and copier data, platform stream tags, host/DAI counter ops, `ipc4-fw-reg.h` shared-memory layout, and DAI link hw_config records for SSP fixup. It is the runtime consumer of topology format decisions and firmware register telemetry.

## Risks and Test Signals
Risks include incorrect trigger order around forks, started/paused reference-count drift after failed IPC, ChainDMA requiring both host and link pipelines to be marked consistently, DAI fixup ambiguity when topology exposes multiple rates/channels, delay errors from invalid stream offsets or counter wrap, and fallback to `-EOPNOTSUPP` disabling precise pointer reporting. Test signals are start/pause/release/stop/hw_free sequences, multi-pipeline priority ordering, xrun/suspend reset behavior, ChainDMA allocation/pause/reset on playback and capture, SSP hw_config selection, ABI-gated delay support, pointer wrap tests, and mixed-rate DAI-to-host frame conversion.
