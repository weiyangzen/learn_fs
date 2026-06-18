# sources/distributed-fs/ceph-client/sound/soc/sof/sof-audio.h

Purpose: Defines the core SOF audio/topology data model and IPC-facing operation tables used by PCM, topology, controls, and PM code.

Important APIs/types: Defines `SOF_AUDIO_PCM_DRV_NAME`, widget classification macros, DAI param constants, mixer volume mapping helpers, `struct sof_ipc_pcm_ops`, `sof_ipc_tplg_control_ops`, `sof_ipc_tplg_widget_ops`, `sof_ipc_tplg_ops`, topology token descriptors, `snd_sof_pcm_stream`, `snd_sof_pcm`, `snd_sof_control`, `snd_sof_dai_link`, `snd_sof_widget`, `snd_sof_pipeline`, `snd_sof_route`, and `snd_sof_dai`. It declares kcontrol, topology load, stream position, widget/route/PCM helpers, token parsers, and PM helpers.

Control flow and integration: IPC implementations fill the ops tables to customize PCM hw_params/trigger/pointer, control IO, widget prepare/setup/free, DAI config, route setup, pipeline completion, manifest parsing, and pipeline restore/tear-down. Runtime code stores topology-derived objects on `snd_sof_dev` lists and uses the declared helpers to find and operate on them.

State and persistence: Structures hold long-lived topology state, runtime PCM state, control cache/dirty state, dynamic widget IDs, pin bindings, queue ID allocators, pipeline counters, route queue IDs, and private IPC-specific data. Most objects live until topology/component removal, while prepared/setup/use-count fields change per stream lifecycle.

Risks: Many fields are touched by both generic and IPC-specific code through `private` pointers, so ownership boundaries must be respected. `snd_sof_find_spcm_dai()` matches DAI link ID to topology `dai_id`; mismatch breaks PCM lookup. Volume conversion assumes monotonic volume maps. Pin binding arrays must match IPC4 max pin constraints.

Test signals: Compile all IPC backends against ops structs, topology token parsing, PCM lookup by DAI/name/component, kcontrol dirty/update paths, volume map boundary values, queue ID allocation, and CONFIG_SND_SOC_SOF_COMPRESS on/off stubs.
