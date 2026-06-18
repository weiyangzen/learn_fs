# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf_mbox.c

Purpose: handles PF-side mailbox protocol for Thunder CPT VFs, translating VF requests into queue length, group binding, priority, and lifecycle state changes.

Important APIs and control flow: `cpt_mbox_intr_handler()` reads pending VF bits from `CPTX_PF_MBOX_INTX`, calls `cpt_handle_mbox_intr()` per VF, and clears each bit. The handler reads mailbox words, handles `CPT_MSG_VF_UP`, `READY`, `VF_DOWN`, `QLEN`, `QBIND_GRP`, and `VQ_PRIORITY`, and responds through `cpt_send_msg_to_vf()` or `cpt_mbox_send_ack()`. Helpers program PF queue control fields through `cpt_cfg_qlen_for_vf()`, `cpt_cfg_vq_priority()`, and `cpt_bind_vq_to_grp()`.

State and persistence: updates `cpt->vfinfo[]` and PF queue registers. `try_module_get()` and `module_put()` pin the PF module while VFs are up.

Dependencies and integration points: depends on PF microcode group state from `cptpf_main.c`, CPT queue control bitfields, and VF mailbox code waiting for ACKs.

Risks and test signals: risks include no explicit NACK for invalid default messages, VF number loops across maximum rather than enabled VF count, unprotected VF state updates, and queue binding failure leaving VF waiters without a typed response. Test signals include READY returning VF ID, QLEN changing PF queue size, group binding returning AE/SE type, priority programming, and module refcount balancing after VF down.
