<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/ext_manifest.h -->
# sources/distributed-fs/ceph-client/include/sound/sof/ext_manifest.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof/ext_manifest.h` is SOF firmware/host ABI
header for IPC3-era audio firmware integration. It defines compile-time message, topology, stream,
debug, trace, PM, manifest, or crash-dump layouts consumed by the Linux SOF driver and DSP firmware.
The source was read as a complete 124-line header for this report.

## Important APIs, Types, and Functions

types: `sof_ext_man_header`, `sof_ext_man_elem_header`, `sof_ext_man_fw_version`,
`sof_ext_man_window`, `sof_ext_man_cc_version`, `ext_man_dbg_abi`, `sof_config_elem`,
`sof_ext_man_config_data`; enums: `sof_ext_man_elem_type`, `config_elem_type`; macros/constants:
`__SOF_FIRMWARE_EXT_MANIFEST_H__`, `SOF_EXT_MAN_MAGIC_NUMBER`, `SOF_EXT_MAN_BUILD_VERSION`,
`SOF_EXT_MAN_VERSION_INCOMPATIBLE`, `SOF_EXT_MAN_VERSION`

## Control Flow

The host constructs packed IPC structures from topology, PCM, PM, or debug requests, sends them
through the SOF mailbox/doorbell path, and firmware replies with matching headers or asynchronous
notifications. These headers describe payloads rather than executing the flow.

## State and Persistence Behavior

State is represented as caller-owned IPC buffers, topology blobs, firmware manifest records, stream
position snapshots, debug windows, or crash data. The header itself owns no persistent storage.

## Dependencies and Integration Points

Direct includes: `linux/bits.h`, `linux/compiler.h`, `linux/types.h`, `sound/sof/info.h`. Integrates
with the SOF Linux driver, topology parser, mailbox IPC transport, and matching DSP firmware ABI.

## Risks and Edge Cases

Risks include ABI drift between host and firmware, missing packing/alignment validation, command IDs
colliding, variable-sized payload bounds errors, and topology/control data that does not match the
active firmware ABI.

## Test Signals

Test structure sizes and offsets, topology loading, IPC command/reply round trips, stream parameter
negotiation, firmware-ready parsing, suspend/resume messages, trace/debug windows, and crash-dump
decoding on matching firmware builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/ext_manifest.h -->
