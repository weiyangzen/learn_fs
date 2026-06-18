# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_mbox.c Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_mbox.c

### Purpose
`otx_cptpf_mbox.c` implements PF-side handling of mailbox messages from OcteonTX CPT VFs. It programs VF queue properties, binds VQs to engine groups, returns VF identity and type data, and ACKs or NACKs control requests.

### Important APIs, Types, And Functions
The public entry point is `otx_cpt_mbox_intr_handler()`. Important helpers are `otx_cpt_handle_mbox_intr()`, `otx_cpt_send_msg_to_vf()`, ACK/NACK helpers, `otx_cpt_clear_mbox_intr()`, `otx_cpt_cfg_qlen_for_vf()`, `otx_cpt_cfg_vq_priority()`, `otx_cpt_bind_vq_to_grp()`, and mailbox debug formatting helpers.

### Control Flow, State, And Persistence
The PF interrupt handler reads the mailbox interrupt bitmap and iterates VFs up to `cpt->max_vfs`. For each asserted bit it reads VF mailbox words, dispatches by opcode, writes responses through PF-to-VF mailbox registers, and clears the interrupt. QLEN updates `PF_QX_CTL.size` and `cont_err`; VQ priority updates `PF_QX_CTL.pri`; group binding validates queue and group bounds, verifies the target group is enabled, writes `PF_QX_CTL.grp`, examines the group or mirrored group's microcode support, and returns the VF engine type. READY returns the VF number, VF_UP returns enabled VF count, PF_TYPE returns PF type, and unsupported binding returns NACK.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on shared mailbox opcodes, PF hardware registers, engine-group state from `otx_cptpf_ucode.c`, and VF polling behavior in `otx_cptvf_mbox.c`. Risks include mailbox register ordering, VF IDs wider than the interrupt bitmap loop type, binding VFs to disabled or mirrored groups, queue-size unit mismatch, and no explicit locking around engine-group reads while SR-IOV state changes. Test signals include VF probe handshake, QLEN/priority/group sysfs changes from VF, invalid group NACK, PF_TYPE query, mailbox interrupt clearing, and debug dumps for each opcode.
