# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cpt_common.h Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cpt_common.h

### Purpose
`otx_cpt_common.h` defines the shared PF/VF mailbox contract and engine type identifiers for the OcteonTX CPT driver family.

### Important APIs, Types, And Functions
Important definitions are `OTX_CPT_MAX_MBOX_DATA_STR_SIZE`, `enum otx_cptpf_type`, `enum otx_cptvf_type`, `enum otx_cpt_mbox_opcode`, and `struct otx_cpt_mbox`. PF types distinguish AE and SE physical functions; VF types distinguish AE and SE engine-group assignments; mailbox opcodes cover VF up/down, readiness, queue length, group binding, priority, PF type query, ACK, and NACK.

### Control Flow, State, And Persistence
No executable state lives here. The definitions persist as ABI-like expectations between `otx_cptpf_mbox.c` and `otx_cptvf_mbox.c`: mailbox register word 0 carries `msg`, word 1 carries `data`, and both sides interpret values through the shared opcode enum.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends only on common Linux types and is included by PF, VF, algorithm, and request-manager code. Risks center on changing opcode numbers or type values, because PF and VF modules communicate through hardware registers rather than typed calls. Test signals include PF/VF readiness handshakes, group binding returning SE or AE type, NACK handling, mailbox debug dumps, and mixed PF/VF module builds.
