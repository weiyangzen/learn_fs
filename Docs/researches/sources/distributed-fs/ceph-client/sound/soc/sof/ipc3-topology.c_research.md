<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-topology.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-topology.c

## Purpose
IPC3 topology translation layer. It parses ALSA topology tokens into SOF IPC3 component, pipeline, route, control, and DAI configuration messages; sets up and tears down DSP widgets and routes; handles keyword-detect DAPM events; and rebuilds/static-tears-down pipelines across verification and suspend/resume.

## Important APIs, Types, and Functions
Defines token tables for PCM, pipeline, scheduler, component, core, UUID, buffers, volume, SRC/ASRC/process, DAI links, HDA/SSP/ALH/DMIC/ESAI/SAI/AFE/ACP/MICFIL/ACP_SDW families, exposed as `ipc3_token_list`. Widget setup helpers include `sof_comp_alloc()`, host/tone/mixer/pipeline/buffer/SRC/ASRC/mux/PGA/process/DAI setup functions, `sof_ipc3_widget_setup()`, and free counterparts. DAI link loaders include HDA, SAI, ESAI, MICFIL, ACP DMIC/BT/SP/HS/SDW, AFE, SSP, DMIC, and ALH. Pipeline/control operations include `sof_ipc3_route_setup()`, control load/setup/free helpers, keyword-detect PCM/trigger/DAPM handlers, `sof_ipc3_complete_pipeline()`, `sof_ipc3_dai_config()`, `sof_ipc3_set_up_all_pipelines()`, `sof_ipc3_tear_down_all_pipelines()`, `sof_ipc3_parse_manifest()`, and `sof_ipc3_link_setup()`. Ops are exported as `ipc3_tplg_ops`.

## Control Flow, State, and Persistence
Topology load creates per-widget private IPC payloads and per-DAI private config (`sof_dai_private_data`) from topology tuples/hw configs. Widget setup sends component, pipeline, buffer, or DAI IPCs to firmware; route setup sends buffer-to-component connections; completion sends `PIPE_COMPLETE`. DAI config persists current hardware config and mutates flags/link DMA/ALH stream IDs during hw_params, triggers, and hw_free. Suspend/verification teardown frees non-scheduler widgets first, handles paused pipelines, then frees schedulers and clears route setup flags. Static pipeline restore recreates widgets, routes, and completion state while respecting firmware ABI differences and dynamic pipeline flags.

## Dependencies and Integration
Depends on ALSA topology token APIs, SOF topology helpers (`sof_update_ipc_object`, widget/route setup wrappers, control lists), IPC3 control ops, PCM params, firmware ABI/version fields, DPCM trigger semantics, and platform-specific DAI formats. Integrated by `ipc3_ops.tplg`, ALSA card topology loading, PCM hw_params/hw_free, and PM suspend/resume.

## Risks and Test Signals
Risks are high because this file bridges topology ABI to firmware ABI: token size/count mismatches, DAI type coverage gaps, ALH index base conversion, SSP validation limits, DMIC ABI backward compatibility, process private data exceeding IPC message size, static versus dynamic pipeline restore differences, and firmware-version-specific scheduler handling. Test signals include topology ABI compatibility tests, topology load for every widget and DAI type, route setup only for IPC3-supported buffer/component links, keyword-detect DAPM start/stop, DAI_CONFIG flag preservation, suspend/resume with running and paused streams, dynamic pipeline override debug flags, and first-boot topology verification/teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-topology.c -->
