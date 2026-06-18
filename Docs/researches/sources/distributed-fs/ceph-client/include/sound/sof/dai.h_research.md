<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/dai.h -->
# sources/distributed-fs/ceph-client/include/sound/sof/dai.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof/dai.h` is SOF firmware/host ABI header for
IPC3-era audio firmware integration. It defines compile-time message, topology, stream, debug,
trace, PM, manifest, or crash-dump layouts consumed by the Linux SOF driver and DSP firmware. The
source was read as a complete 132-line header for this report.

## Important APIs, Types, and Functions

types: `sof_ipc_dai_config`, `sof_dai_private_data`; enums: `sof_ipc_dai_type`; macros/constants:
`__INCLUDE_SOUND_SOF_DAI_H__`, `SOF_DAI_FMT_I2S`, `SOF_DAI_FMT_RIGHT_J`, `SOF_DAI_FMT_LEFT_J`,
`SOF_DAI_FMT_DSP_A`, `SOF_DAI_FMT_DSP_B`, `SOF_DAI_FMT_PDM`, `SOF_DAI_FMT_CONT`,
`SOF_DAI_FMT_GATED`, `SOF_DAI_FMT_NB_NF`, `SOF_DAI_FMT_NB_IF`, `SOF_DAI_FMT_IB_NF`,
`SOF_DAI_FMT_IB_IF`, `SOF_DAI_FMT_CBP_CFP`, and 19 more

## Control Flow

The host constructs packed IPC structures from topology, PCM, PM, or debug requests, sends them
through the SOF mailbox/doorbell path, and firmware replies with matching headers or asynchronous
notifications. These headers describe payloads rather than executing the flow.

## State and Persistence Behavior

State is represented as caller-owned IPC buffers, topology blobs, firmware manifest records, stream
position snapshots, debug windows, or crash data. The header itself owns no persistent storage.

## Dependencies and Integration Points

Direct includes: `sound/sof/header.h`, `sound/sof/dai-intel.h`, `sound/sof/dai-imx.h`,
`sound/sof/dai-amd.h`, `sound/sof/dai-mediatek.h`. Integrates with the SOF Linux driver, topology
parser, mailbox IPC transport, and matching DSP firmware ABI.

## Risks and Edge Cases

Risks include ABI drift between host and firmware, missing packing/alignment validation, command IDs
colliding, variable-sized payload bounds errors, and topology/control data that does not match the
active firmware ABI.

## Test Signals

Test structure sizes and offsets, topology loading, IPC command/reply round trips, stream parameter
negotiation, firmware-ready parsing, suspend/resume messages, trace/debug windows, and crash-dump
decoding on matching firmware builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/dai.h -->
