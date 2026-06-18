# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-topology.h

## Purpose
Private IPC4 topology data contract for SOF. It defines the module, pipeline, copier, control, gain, mixer, SRC, ASRC, process, DMA, gateway, audio format, queue, and ChainDMA structures shared by IPC4 topology, controls, and PCM code.

## APIs, Types, and Functions
Defines constants for firmware pages/object sizes, module type bits, sample types, node IDs, gain volume, DMA limits, ChainDMA sentinel IDs and buffer sizes, ALH multi-gateway ranges, and IPC4 control parameter IDs. Important types include `sof_ipc4_pipeline`, `ipc4_pipeline_set_state_data`, `sof_ipc4_pin_format`, `sof_ipc4_available_audio_format`, `sof_copier_gateway_cfg`, `sof_ipc4_copier_data`, `sof_ipc4_copier`, DMA config/TLV structs, `sof_ipc4_control_data`, `sof_ipc4_control_msg_payload`, `sof_ipc4_gain(_data/_params)`, `sof_ipc4_mixer`, `sof_ipc4_src`, `sof_ipc4_asrc`, `sof_ipc4_base_module_cfg_ext`, and `sof_ipc4_process`. It declares `sof_ipc4_copier_is_single_bitdepth()`.

## Control Flow, State, and Persistence
The header has no logic, but its structs are persistent runtime state. Topology setup allocates these as `swidget->private`, DAI private data, or `scontrol->ipc_control_data`; PCM trigger code reads pipeline state and ChainDMA fields; controls read/write control payloads; route setup uses pin counts, node ids and gateway formats; prepare/unprepare paths allocate and free IPC payload buffers referenced by copier/process records.

## Dependencies and Integration
Includes IPC4 base headers and is included by `ipc4-topology.c`, `ipc4-control.c`, and `ipc4-pcm.c`. It ties topology token parsing to firmware IPC payload layouts, ASoC DAPM widget types, SOF firmware manifest metadata, and firmware register/pipeline runtime behavior.

## Risks and Test Signals
Risks include ABI-sensitive packing, flexible-array sizing mistakes, bitfield/node-id macro misuse, object-size constants diverging from firmware memory accounting, and ownership confusion around pointers such as `copier_config`, `ipc_config_data`, and pin-format arrays. Test signals are `struct_size()` allocation checks, KASAN/KMEMLEAK during topology load/unload, route setup with multi-pin modules, ChainDMA and normal copier paths, firmware accepting generated IPC payloads, and build coverage when IPC4 header definitions change.
