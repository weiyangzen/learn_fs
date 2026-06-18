# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_mbox.c Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_mbox.c

### Purpose
`otx_cptvf_mbox.c` implements VF-side mailbox communication with the OcteonTX CPT PF. It sends synchronous control messages, handles PF replies in the misc interrupt path, and stores PF-provided VF identity, VF count, and engine type.

### Important APIs, Types, And Functions
Public functions are `otx_cptvf_handle_mbox_intr()`, `otx_cptvf_check_pf_ready()`, `otx_cptvf_send_vq_size_msg()`, `otx_cptvf_send_vf_to_grp_msg()`, `otx_cptvf_send_vf_priority_msg()`, `otx_cptvf_send_vf_up()`, and `otx_cptvf_send_vf_down()`. Internal helpers include `cptvf_send_msg_to_pf()`, `cptvf_send_msg_to_pf_timeout()`, and mailbox debug formatting.

### Control Flow, State, And Persistence
Sending clears `pf_acked` and `pf_nacked`, writes message and data to VF-to-PF mailbox registers, then polls up to two seconds in 10 ms sleeps for an interrupt handler to set either flag. The interrupt handler reads the PF mailbox words and updates state: READY stores `vfid`, QBIND_GRP stores `vftype`, VF_UP stores `num_vfs`, ACK sets `pf_acked`, and NACK sets `pf_nacked`. Group messages update `vfgrp` only after a successful PF response.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on PF mailbox opcode semantics, VF misc interrupts being enabled before synchronous waits, sleepable probe/sysfs contexts, and MMIO register ordering. Risks include polling flags without completions or barriers, timeout if interrupts are masked, no serialization around concurrent sysfs mailbox sends, and comments that misstate VF_DOWN as UP. Test signals include READY during probe, QLEN and priority ACK, group bind success and NACK, PF not responding, VF_DOWN during remove, and mailbox debug dumps.
