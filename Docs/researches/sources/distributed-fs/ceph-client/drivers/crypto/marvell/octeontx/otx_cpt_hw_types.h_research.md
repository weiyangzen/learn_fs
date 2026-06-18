# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cpt_hw_types.h Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cpt_hw_types.h

### Purpose
`otx_cpt_hw_types.h` is the OcteonTX CPT hardware register and descriptor map. It provides PCI IDs, BAR indices, register offsets, interrupt masks, instruction/result layouts, queue-control bitfields, completion codes, and hardware error-code formats used by PF and VF drivers.

### Important APIs, Types, And Functions
Important constants include PF/VF PCI IDs, BAR selectors, PF/VF MSI-X vector counts, mailbox interrupt offsets, `OTX_CPT_MAX_ENGINE_GROUPS`, `OTX_CPT_INST_SIZE`, queue chunk pointer size, VF interrupt masks, and PF/VF register offset macros. Key enums and unions are `enum otx_cpt_ucode_error_code_e`, `enum otx_cpt_comp_e`, `enum otx_cpt_vf_int_vec_e`, `union otx_cpt_inst_s`, `union otx_cpt_res_s`, `union otx_cptx_pf_bist_status`, `union otx_cptx_pf_constants`, `union otx_cptx_pf_exe_bist_status`, `union otx_cptx_pf_qx_ctl`, `union otx_cptx_vqx_saddr`, interrupt enable/status unions, doorbell, done, done-wait, queue-control, and `union otx_cpt_error_code`.

### Control Flow, State, And Persistence
The header has no functions but dictates how runtime code programs hardware. PF probe reads BIST and constants, PF mailbox writes `PF_QX_CTL`, VF probe configures queue base, doorbell, done coalescing, and interrupts, and the request manager fills `CPT_INST_S` and parses `CPT_RES_S` plus microcode error codes. Bitfield definitions are endian-conditional and must match hardware wire layout.

### Dependencies, Integration Points, Risks, And Test Signals
All OcteonTX CPT C files depend on this header. Risks include incorrect bitfield layout on big-endian builds, queue size units in 64-bit words versus instruction count, doorbell units as eight 64-bit words per instruction, result alignment expectations, and stale register offsets. Test signals include PF BIST failure reporting, queue control programming from mailbox QLEN/group/priority, VF misc and done interrupts, request completion-code handling, doorbell overflow paths, and endian build coverage.
