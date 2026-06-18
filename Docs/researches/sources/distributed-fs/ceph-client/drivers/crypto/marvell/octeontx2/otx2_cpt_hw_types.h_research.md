# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_hw_types.h

## Purpose
This header is the hardware contract for the Marvell OcteonTX2/CN10K CPT crypto accelerator driver. It defines PCI IDs, MSI-X vector counts, mailbox interrupt offsets, CPT PF/LF/RVU register offsets, hardware completion codes, and packed register/instruction/result layouts used by both PF and VF code.

## Important APIs, types, and constants
Key constants include `OTX2_CPT_PCI_PF_DEVICE_ID`, `OTX2_CPT_PCI_VF_DEVICE_ID`, `CN10K_CPT_PCI_*`, `OTX2_CPT_MAX_ENGINE_GROUPS`, `OTX2_CPT_INST_SIZE`, `OTX2_CPT_LF_MSIX_VECTORS`, and register macros such as `OTX2_CPT_LF_Q_BASE`, `OTX2_CPT_LF_NQX()`, `OTX2_CPT_PF_VFX_MBOXX()`, and `OTX2_CPT_LMT_LF_LMTLINEX()`. `enum otx2_cpt_comp_e` maps hardware completion states, while `enum otx2_cpt_ucode_comp_code_e` maps selected microcode errors. Core ABI types are `union otx2_cpt_inst_s`, `union otx2_cpt_res_s`, `union otx2_cptx_lf_ctl`, `union otx2_cptx_lf_done_wait`, `union otx2_cptx_lf_inprog`, `union otx2_cptx_lf_q_base`, `union otx2_cptx_lf_q_size`, and `union otx2_cptx_af_lf_ctrl`.

## Control flow and integration
This file has no executable control flow, but it controls how executable code writes registers and interprets hardware memory. `otx2_cptlf.h` uses LF queue register unions to enable queues, set queue base/size, and fill CPT instructions. `otx2_cptvf_reqmgr.c` polls `otx2_cpt_res_s` completion codes. PF microcode code uses AF register offsets from common RVU headers plus the completion/result definitions here. PF and VF probe tables use the device IDs.

## State and persistence
State represented here lives either in MMIO registers or DMA-visible command/result memory. Queue enablement, done counts, in-flight counts, engine group masks, and instruction/result buffers are transient hardware state; there is no disk persistence. Bitfield layout and endian assumptions are persistent ABI requirements across the driver and firmware.

## Dependencies and integration points
The header depends only on Linux integer types but is consumed by PF, VF, LF, mailbox, request manager, and algorithm paths. It also implicitly depends on RVU mailbox definitions and Marvell register addressing conventions used in `rvu_reg.h` and `otx2_cpt_common.h`.

## Risks and edge cases
The largest risk is ABI drift: bitfield ordering, register offsets, alignment, or completion-code interpretation changes would break DMA commands or MMIO programming. `union otx2_cpt_res_s` differs between CN9K and CN10K layouts, so hardware-operation callbacks must choose the correct completion-code accessor. Queue control comments require quiescent writes; callers must respect these ordering rules.

## Test signals
Useful signals include successful PF/VF probe on OTX2 and CN10K devices, LF queue enable/disable without hardware warnings, completion-code decoding for success/fault/hardware/instruction errors, mailbox interrupt delivery, and crypto self-tests covering both CN9K and CN10K result layouts.
