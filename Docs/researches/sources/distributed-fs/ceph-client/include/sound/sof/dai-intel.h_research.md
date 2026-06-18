<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/dai-intel.h -->
# sources/distributed-fs/ceph-client/include/sound/sof/dai-intel.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof/dai-intel.h` is SOF IPC3 DAI parameter ABI
header for INTEL platform links. It supplies packed configuration payloads embedded by
`sof_ipc_dai_config` for the vendor DAI backend. The source was read as a complete 205-line header
for this report.

## Important APIs, Types, and Functions

types: `sof_ipc_dai_ssp_params`, `sof_ipc_dai_hda_params`, `sof_ipc_dai_alh_params`,
`sof_ipc_dai_dmic_pdm_ctrl`, `sof_ipc_dai_dmic_params`; macros/constants:
`__INCLUDE_SOUND_SOF_DAI_INTEL_H__`, `SOF_DAI_INTEL_SSP_QUIRK_TINTE`,
`SOF_DAI_INTEL_SSP_QUIRK_PINTE`, `SOF_DAI_INTEL_SSP_QUIRK_SMTATF`, `SOF_DAI_INTEL_SSP_QUIRK_MMRATF`,
`SOF_DAI_INTEL_SSP_QUIRK_PSPSTWFDFD`, `SOF_DAI_INTEL_SSP_QUIRK_PSPSRWFDFD`,
`SOF_DAI_INTEL_SSP_QUIRK_LBM`, `SOF_DAI_INTEL_SSP_FRAME_PULSE_WIDTH_MAX`,
`SOF_DAI_INTEL_SSP_SLOT_PADDING_MAX`, `SOF_DAI_INTEL_SSP_MCLK_0_DISABLE`,
`SOF_DAI_INTEL_SSP_MCLK_1_DISABLE`, `SOF_DAI_INTEL_SSP_CLKCTRL_MCLK_KA`,
`SOF_DAI_INTEL_SSP_CLKCTRL_BCLK_KA`, and 6 more

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/dai-intel.h -->
