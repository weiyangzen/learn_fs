# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/src/pipeline.c

Purpose: implements pipeline lifecycle, SP thread mapping, stage allocation/linking, start/stop events, output stage lookup, and port configuration.

Important functions/state: static `pipeline_num_to_sp_thread_map[20]` and `pipeline_sp_thread_list[SH_CSS_MAX_SP_THREADS]`; public init/create/map/destroy/start/request_stop/clean/add/finalize/get/status APIs; private stage destroy/create, defaults, zoom-stage selection, and in/out port config.

Control flow: module init resets maps. Stage addition validates descriptor, supplies previous output as input for eligible ISP stages, creates a stage, auto-allocates missing output/VF frames, and links it. Finalize assigns stage numbers, chooses zoom stage by pipe id, and encodes port sources/sinks for continuous/offline modes. Start initializes SP pipeline and enqueues start stream event; stop enqueues stop and uninitializes SP pipeline.

State/persistence: global pipe-to-thread maps persist. Pipelines own linked stage nodes and any frames marked allocated.

Dependencies/integration: HMM/frame allocation, buffer queue PSYS events, SP pipeline init/uninit/status, ISP params, debug tracing, and pipe/binary metadata.

Risks: mapping is unsynchronized and assert-heavy. `ia_css_pipeline_start` uses local `pipe_num = 0` instead of `pipeline->pipe_num`, which can surprise multi-pipe users. Firmware VF allocation path references `binary->vf_frame_info` even when firmware is present, a potential null issue.

Test signals: multi-pipeline map/unmap, stage auto-allocation cleanup on failure, continuous/offline port config bits per pipe id, start/stop when SP is stopped, and `has_stopped` with SP group DMEM state.
