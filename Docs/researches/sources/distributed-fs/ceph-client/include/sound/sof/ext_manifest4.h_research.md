<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/ext_manifest4.h -->
# sources/distributed-fs/ceph-client/include/sound/sof/ext_manifest4.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof/ext_manifest4.h` is SOF firmware/host ABI
header for IPC3-era audio firmware integration. It defines compile-time message, topology, stream,
debug, trace, PM, manifest, or crash-dump layouts consumed by the Linux SOF driver and DSP firmware.
The source was read as a complete 119-line header for this report.

## Important APIs, Types, and Functions

types: `sof_ext_manifest4_hdr`, `sof_man4_fw_binary_header`, `sof_man4_segment_desc`,
`sof_man4_module`, `sof_man4_module_config`; macros/constants: `__SOF_FIRMWARE_EXT_MANIFEST4_H__`,
`SOF_EXT_MAN4_MAGIC_NUMBER`, `MAX_MODULE_NAME_LEN`, `MAX_FW_BINARY_NAME`, `DEFAULT_HASH_SHA256_LEN`,
`SOF_MAN4_FW_HDR_OFFSET`, `SOF_MAN4_FW_HDR_OFFSET_CAVS_1_5`

## Control Flow

The host constructs packed IPC structures from topology, PCM, PM, or debug requests, sends them
through the SOF mailbox/doorbell path, and firmware replies with matching headers or asynchronous
notifications. These headers describe payloads rather than executing the flow.

## State and Persistence Behavior

State is represented as caller-owned IPC buffers, topology blobs, firmware manifest records, stream
position snapshots, debug windows, or crash data. The header itself owns no persistent storage.

## Dependencies and Integration Points

Direct includes: `linux/uuid.h`. Integrates with the SOF Linux driver, topology parser, mailbox IPC
transport, and matching DSP firmware ABI.

## Risks and Edge Cases

Risks include ABI drift between host and firmware, missing packing/alignment validation, command IDs
colliding, variable-sized payload bounds errors, and topology/control data that does not match the
active firmware ABI.

## Test Signals

Test structure sizes and offsets, topology loading, IPC command/reply round trips, stream parameter
negotiation, firmware-ready parsing, suspend/resume messages, trace/debug windows, and crash-dump
decoding on matching firmware builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/ext_manifest4.h -->
