<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/stream.h -->
# sources/distributed-fs/ceph-client/include/sound/sof/stream.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof/stream.h` is SOF firmware/host ABI header for
IPC3-era audio firmware integration. It defines compile-time message, topology, stream, debug,
trace, PM, manifest, or crash-dump layouts consumed by the Linux SOF driver and DSP firmware. The
source was read as a complete 151-line header for this report.

## Important APIs, Types, and Functions

types: `sof_ipc_host_buffer`, `sof_ipc_stream_params`, `sof_ipc_pcm_params`,
`sof_ipc_pcm_params_reply`, `sof_ipc_stream`, `sof_ipc_stream_posn`; enums: `sof_ipc_frame`,
`sof_ipc_buffer_format`, `sof_ipc_stream_direction`; macros/constants:
`__INCLUDE_SOUND_SOF_STREAM_H__`, `SOF_IPC_MAX_CHANNELS`, `SOF_RATE_8000`, `SOF_RATE_11025`,
`SOF_RATE_12000`, `SOF_RATE_16000`, `SOF_RATE_22050`, `SOF_RATE_24000`, `SOF_RATE_32000`,
`SOF_RATE_44100`, `SOF_RATE_48000`, `SOF_RATE_64000`, `SOF_RATE_88200`, `SOF_RATE_96000`, and 17
more

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/stream.h -->
