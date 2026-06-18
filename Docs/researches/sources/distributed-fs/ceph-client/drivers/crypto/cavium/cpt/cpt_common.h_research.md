# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cpt_common.h

Purpose: provides common Thunder CPT PF/VF constants, register address macros, mailbox opcodes, state flags, and 64-bit CSR accessors.

Important APIs and types: device IDs `CPT_81XX_PCI_PF_DEVICE_ID` and `CPT_81XX_PCI_VF_DEVICE_ID`, flags `CPT_FLAG_SRIOV_ENABLED`, `CPT_FLAG_VF_DRIVER`, and `CPT_FLAG_DEVICE_READY`, mailbox opcodes `CPT_MSG_*`, `struct cpt_mbox`, and `cpt_write_csr64()`/`cpt_read_csr64()`. Register macros cover PF global, mailbox, engine, queue, and VF queue spaces such as `CPTX_PF_QX_CTL()`, `CPTX_PF_VFX_MBOXX()`, `CPTX_VQX_*()`, and `CPTX_VFX_PF_MBOXX()`.

Control flow and state: this is a header-only ABI layer; state lives in hardware registers and in PF/VF structs. Register offsets encode CPT instance, queue/VF indices, and mailbox words.

Dependencies and integration points: depends on PCI, delay, byteorder, and `cpt_hw_types.h` bitfield overlays. Every CPT PF/VF source includes it for CSR and mailbox access.

Risks and test signals: risks include incorrect offset arithmetic causing PF/VF register aliasing, W1C/W1S misuse by callers, and flag checks being non-atomic. Test signals include mailbox round trips, PF queue programming visible to VFs, CSR reads matching hardware documentation, and no register access outside mapped BAR0.
