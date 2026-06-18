<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/topology.h -->
# sources/distributed-fs/ceph-client/include/sound/sof/topology.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof/topology.h` is SOF firmware/host ABI header
for IPC3-era audio firmware integration. It defines compile-time message, topology, stream, debug,
trace, PM, manifest, or crash-dump layouts consumed by the Linux SOF driver and DSP firmware. The
source was read as a complete 310-line header for this report.

## Important APIs, Types, and Functions

types: `sof_ipc_comp`, `sof_ipc_buffer`, `sof_ipc_comp_config`, `sof_ipc_comp_host`,
`sof_ipc_comp_dai`, `sof_ipc_comp_mixer`, `sof_ipc_comp_volume`, `sof_ipc_comp_src`,
`sof_ipc_comp_asrc`, `sof_ipc_comp_mux`, `sof_ipc_comp_tone`, `sof_ipc_comp_process`,
`sof_ipc_free`, `sof_ipc_comp_reply`, and 4 more; enums: `sof_comp_type`, `sof_volume_ramp`,
`sof_ipc_process_type`, `sof_ipc_pipe_sched_time_domain`, `sof_event_types`; macros/constants:
`__INCLUDE_SOUND_SOF_TOPOLOGY_H__`, `SOF_XRUN_STOP`, `SOF_XRUN_UNDER_ZERO`, `SOF_XRUN_OVER_NULL`,
`SOF_MEM_CAPS_RAM`, `SOF_MEM_CAPS_ROM`, `SOF_MEM_CAPS_EXT`, `SOF_MEM_CAPS_LP`, `SOF_MEM_CAPS_HP`,
`SOF_MEM_CAPS_DMA`, `SOF_MEM_CAPS_CACHE`, `SOF_MEM_CAPS_EXEC`, `SOF_MEM_CAPS_L3`,
`SOF_BUF_OVERRUN_PERMITTED`, and 2 more

## Control Flow

The host constructs packed IPC structures from topology, PCM, PM, or debug requests, sends them
through the SOF mailbox/doorbell path, and firmware replies with matching headers or asynchronous
notifications. These headers describe payloads rather than executing the flow.

## State and Persistence Behavior

State is represented as caller-owned IPC buffers, topology blobs, firmware manifest records, stream
position snapshots, debug windows, or crash data. The header itself owns no persistent storage.

## Dependencies and Integration Points

Direct includes: `sound/sof/header.h`. Integrates with the SOF Linux driver, topology parser,
mailbox IPC transport, and matching DSP firmware ABI.

## Risks and Edge Cases

Risks include ABI drift between host and firmware, missing packing/alignment validation, command IDs
colliding, variable-sized payload bounds errors, and topology/control data that does not match the
active firmware ABI.

## Test Signals

Test structure sizes and offsets, topology loading, IPC command/reply round trips, stream parameter
negotiation, firmware-ready parsing, suspend/resume messages, trace/debug windows, and crash-dump
decoding on matching firmware builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/topology.h -->
