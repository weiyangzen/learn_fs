<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/dai-amd.h -->
# sources/distributed-fs/ceph-client/include/sound/sof/dai-amd.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof/dai-amd.h` is SOF IPC3 DAI parameter ABI
header for AMD platform links. It supplies packed configuration payloads embedded by
`sof_ipc_dai_config` for the vendor DAI backend. The source was read as a complete 36-line header
for this report.

## Important APIs, Types, and Functions

types: `sof_ipc_dai_acp_params`, `sof_ipc_dai_acpdmic_params`, `sof_ipc_dai_acp_sdw_params`;
macros/constants: `__INCLUDE_SOUND_SOF_DAI_AMD_H__`

## Control Flow

Topology or machine-driver data is translated into DAI-specific IPC fields, then
`SOF_IPC_DAI_CONFIG` carries those fields to firmware during hw_params, hw_free, pause, or setup
stages. Firmware reads the union member selected by the generic DAI type.

## State and Persistence Behavior

No storage is owned here. The fields persist only inside topology private data, host IPC messages,
and firmware-side DAI configuration while the pipeline or link is active.

## Dependencies and Integration Points

Direct includes: `sound/sof/header.h`. Integrates with the SOF Linux driver, topology parser,
mailbox IPC transport, and matching DSP firmware ABI.

## Risks and Edge Cases

Risks include platform driver and firmware disagreeing on packed field order, clock polarity or TDM
slot mistakes, invalid reserved fields, and adding fields without preserving ABI compatibility.

## Test Signals

Test topology parsing, IPC payload size/layout checks, hw_params and hw_free DAI_CONFIG messages,
vendor-specific clocking and TDM modes, and firmware rejection of invalid parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/dai-amd.h -->
