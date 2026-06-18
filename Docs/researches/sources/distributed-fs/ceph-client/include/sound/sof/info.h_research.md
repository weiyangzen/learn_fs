<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/info.h -->
# sources/distributed-fs/ceph-client/include/sound/sof/info.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof/info.h` is SOF firmware/host ABI header for
IPC3-era audio firmware integration. It defines compile-time message, topology, stream, debug,
trace, PM, manifest, or crash-dump layouts consumed by the Linux SOF driver and DSP firmware. The
source was read as a complete 144-line header for this report.

## Important APIs, Types, and Functions

types: `sof_ipc_fw_version`, `sof_ipc_fw_ready`, `sof_ipc_ext_data_hdr`, `sof_ipc_window_elem`,
`sof_ipc_window`, `sof_ipc_cc_version`, `sof_ipc_probe_support`, `sof_ipc_user_abi_version`; enums:
`sof_ipc_ext_data`, `sof_ipc_region`; macros/constants: `__INCLUDE_SOUND_SOF_INFO_H__`,
`SOF_IPC_MAX_ELEMS`, `SOF_IPC_INFO_BUILD`, `SOF_IPC_INFO_LOCKS`, `SOF_IPC_INFO_LOCKSV`,
`SOF_IPC_INFO_GDB`, `SOF_IPC_INFO_D3_PERSISTENT`, `SOF_FW_VER`

## Control Flow

The host constructs packed IPC structures from topology, PCM, PM, or debug requests, sends them
through the SOF mailbox/doorbell path, and firmware replies with matching headers or asynchronous
notifications. These headers describe payloads rather than executing the flow.

## State and Persistence Behavior

State is represented as caller-owned IPC buffers, topology blobs, firmware manifest records, stream
position snapshots, debug windows, or crash data. The header itself owns no persistent storage.

## Dependencies and Integration Points

Direct includes: `sound/sof/header.h`, `sound/sof/stream.h`. Integrates with the SOF Linux driver,
topology parser, mailbox IPC transport, and matching DSP firmware ABI.

## Risks and Edge Cases

Risks include ABI drift between host and firmware, missing packing/alignment validation, command IDs
colliding, variable-sized payload bounds errors, and topology/control data that does not match the
active firmware ABI.

## Test Signals

Test structure sizes and offsets, topology loading, IPC command/reply round trips, stream parameter
negotiation, firmware-ready parsing, suspend/resume messages, trace/debug windows, and crash-dump
decoding on matching firmware builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/info.h -->
