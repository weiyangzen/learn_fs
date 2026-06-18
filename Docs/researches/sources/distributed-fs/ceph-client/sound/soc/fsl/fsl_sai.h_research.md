# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_sai.h

## Purpose
`fsl_sai.h` defines the register map, bit fields, constants, SoC data, version/parameter descriptors, dataline configuration, and private state for the Freescale/NXP SAI driver. It is the contract used by `fsl_sai.c` to translate ALSA DAI operations into register writes.

## Important APIs, Types, And Functions
There are no exported functions. The file provides register address macros like `FSL_SAI_TCSR(ofs)`, `FSL_SAI_RCR4(ofs)`, `FSL_SAI_xCR*`, `FSL_SAI_xDR0`, and `FSL_SAI_xMR`; control bit masks such as `FSL_SAI_CSR_TERE`, `FSL_SAI_CR2_BCD_MSTR`, `FSL_SAI_CR4_FRSZ`, `FSL_SAI_CR5_WNW`, and timestamp counter fields; and audio capability constants such as `FSL_SAI_FORMATS`, `FSL_SAI_MCLK_MAX`, and maxburst defaults.

The key types are `struct fsl_sai_soc_data`, `struct fsl_sai_verid`, `struct fsl_sai_param`, `struct fsl_sai_dl_cfg`, and `struct fsl_sai`. `TX` and `RX` are direction indexes used throughout the C file.

## Control Flow
The header itself has no runtime flow, but its macros encode how the driver selects offset-0 vs offset-8 register layouts, how Tx/Rx symmetric operations share code through `FSL_SAI_x*` selectors, how MCLK sources are selected through CR2/MCTL masks, and how FIFO, frame, sync, and timestamp operations are programmed.

## State And Persistence
`struct fsl_sai` contains the driver lifetime state: platform device, regmap, clocks, resource, stream mode flags, dataline configuration pointer/count, selected MCLK IDs, stream counters, slots, slot widths, DMA data, SoC data, hardware version data, PM QoS state, pinctrl state, SDMA peripheral configs, and constrained-rate storage. This state persists for the platform device lifetime and is used to reconstruct hardware state after runtime PM.

## Dependencies And Integration Points
The header depends on Linux DMA and ALSA DMAEngine PCM types. It is tightly coupled to ASoC DAI callbacks, regmap register programming, device-tree SoC match data, SDMA peripheral configuration, pinctrl, runtime PM, and timestamp kcontrols in `fsl_sai.c`.

## Risks And Edge Cases
Register macros must stay aligned with hardware revisions; an incorrect `reg_offset`, `max_register`, or volatile/writeable decision in the C file can cause regmap caching or access failures. `FAL_SAI_NUM_RATES` must remain large enough for constrained-rate output. `struct fsl_sai_dl_cfg` assumes up to eight datalines, so future hardware with more lanes would need expanded masks and parsing.

## Test Signals
Compile coverage should catch missing field or macro changes. Runtime signals include correct regmap access on all compatible devices, correct rate constraints, valid multi-dataline DMA addressing, and working timestamp controls where `FSL_SAI_VERID_TSTMP_EN` is set.
