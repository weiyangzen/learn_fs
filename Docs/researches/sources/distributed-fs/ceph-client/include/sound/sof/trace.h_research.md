<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/trace.h -->
# sources/distributed-fs/ceph-client/include/sound/sof/trace.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof/trace.h` is SOF firmware/host ABI header for
IPC3-era audio firmware integration. It defines compile-time message, topology, stream, debug,
trace, PM, manifest, or crash-dump layouts consumed by the Linux SOF driver and DSP firmware. The
source was read as a complete 107-line header for this report.

## Important APIs, Types, and Functions

types: `sof_ipc_dma_trace_params`, `sof_ipc_dma_trace_params_ext`, `sof_ipc_dma_trace_posn`,
`sof_ipc_trace_filter_elem`, `sof_ipc_trace_filter`, `sof_ipc_panic_info`; macros/constants:
`__INCLUDE_SOUND_SOF_TRACE_H__`, `SOF_TRACE_FILENAME_SIZE`, `SOF_IPC_TRACE_FILTER_ELEM_SET_LEVEL`,
`SOF_IPC_TRACE_FILTER_ELEM_BY_UUID`, `SOF_IPC_TRACE_FILTER_ELEM_BY_PIPE`,
`SOF_IPC_TRACE_FILTER_ELEM_BY_COMP`, `SOF_IPC_TRACE_FILTER_ELEM_FIN`, `SOF_IPC_PANIC_MAGIC`,
`SOF_IPC_PANIC_MAGIC_MASK`, `SOF_IPC_PANIC_CODE_MASK`, `SOF_IPC_PANIC_MEM`, `SOF_IPC_PANIC_WORK`,
`SOF_IPC_PANIC_IPC`, `SOF_IPC_PANIC_ARCH`, and 8 more

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/trace.h -->
