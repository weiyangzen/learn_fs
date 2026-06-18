<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/control.h -->
# sources/distributed-fs/ceph-client/include/sound/sof/control.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof/control.h` is SOF firmware/host ABI header for
IPC3-era audio firmware integration. It defines compile-time message, topology, stream, debug,
trace, PM, manifest, or crash-dump layouts consumed by the Linux SOF driver and DSP firmware. The
source was read as a complete 158-line header for this report.

## Important APIs, Types, and Functions

types: `sof_ipc_ctrl_value_chan`, `sof_ipc_ctrl_value_comp`, `sof_ipc_ctrl_data`,
`sof_ipc_comp_event`; enums: `sof_ipc_chmap`, `sof_ipc_ctrl_type`, `sof_ipc_ctrl_cmd`,
`sof_ipc_ctrl_event_type`; macros/constants: `__INCLUDE_SOUND_SOF_CONTROL_H__`

## Control Flow

The host constructs packed IPC structures from topology, PCM, PM, or debug requests, sends them
through the SOF mailbox/doorbell path, and firmware replies with matching headers or asynchronous
notifications. These headers describe payloads rather than executing the flow.

## State and Persistence Behavior

State is represented as caller-owned IPC buffers, topology blobs, firmware manifest records, stream
position snapshots, debug windows, or crash data. The header itself owns no persistent storage.

## Dependencies and Integration Points

Direct includes: `uapi/sound/sof/header.h`, `sound/sof/header.h`. Integrates with the SOF Linux
driver, topology parser, mailbox IPC transport, and matching DSP firmware ABI.

## Risks and Edge Cases

Risks include ABI drift between host and firmware, missing packing/alignment validation, command IDs
colliding, variable-sized payload bounds errors, and topology/control data that does not match the
active firmware ABI.

## Test Signals

Test structure sizes and offsets, topology loading, IPC command/reply round trips, stream parameter
negotiation, firmware-ready parsing, suspend/resume messages, trace/debug windows, and crash-dump
decoding on matching firmware builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/control.h -->
