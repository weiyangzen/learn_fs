# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-priv.h

## Purpose
Private IPC4 integration header for the SOF core. It defines IPC4-specific firmware/library/module state, fixed mailbox/debug window indices, mtrace capability enum, shared operation tables, and cross-file helper prototypes.

## APIs, Types, and Functions
Defines `enum sof_ipc4_mtrace_type`, `struct sof_ipc4_fw_module`, `struct sof_ipc4_fw_library`, and `struct sof_ipc4_fw_data`. It declares operation tables `ipc4_loader_ops`, `ipc4_tplg_ops`, `tplg_ipc4_control_ops`, `ipc4_pcm_ops`, and `ipc4_mtrace_ops`, plus helpers for pipeline state, mtrace position, split release completion, firmware configuration query, library reload, module lookup by UUID, active widget lookup by module/instance ids, CPC update, debug slot lookup by type, mic privacy change, and pipeline-state string formatting.

## Control Flow, State, and Persistence
`sof_ipc4_fw_data` is the persistent per-device IPC4 state stored in `sdev->private`. It carries the firmware manifest header offset, xarray of loaded firmware libraries, optional NHLT data, mtrace type and log size, playback/capture DMA counts, maximum pipeline/library counts, context-save and library-restore flags, platform library-loading and mic-privacy callbacks, and `pipeline_state_mutex` used by runtime trigger and pipeline deletion paths.

## Dependencies and Integration
Includes Linux IDR/IDA and IPC4 manifest/header definitions, plus SOF private state. All implementation files in this subset include it to share state and exported ops. Platform-specific SOF code fills callback fields and capability values before IPC4 loader, topology, PCM, and tracing code consume them.

## Risks and Test Signals
Risks are mostly contract drift: a field updated by platform code may be assumed initialized by topology/PCM/tracing, `fw_lib_xa` lifetime must outlive module-private pointers, and `pipeline_state_mutex` must cover every path that mutates pipeline ref counts or firmware state. Test signals are full IPC4 probe/boot, library xarray lifecycle, suspend/resume with context save, mtrace capability gating, concurrent trigger serialization, and build coverage for all declared cross-file helpers.
