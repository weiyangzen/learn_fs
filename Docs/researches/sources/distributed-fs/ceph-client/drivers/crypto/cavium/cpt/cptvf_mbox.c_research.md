# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_mbox.c

Purpose: implements VF-side synchronous mailbox communication with the CPT PF.

Important APIs and control flow: `cptvf_send_msg_to_pf()` writes mailbox words to trigger a PF interrupt. `cptvf_handle_mbox_intr()` reads PF responses and updates `pf_acked`, `pf_nacked`, `vfid`, and `vftype`. `cptvf_send_msg_to_pf_timeout()` sends a message then polls up to `CPT_MBOX_MSG_TIMEOUT`, returning `-EINVAL` on NACK and `-EBUSY` on timeout. Public wrappers send READY, QLEN, group binding, priority, VF_UP, and VF_DOWN messages.

State and persistence: mailbox state is two booleans and negotiated VF identity/type in `struct cpt_vf`; persistent hardware state is PF-programmed queue config in response to messages.

Dependencies and integration points: used by `cptvf_main.c` during probe/remove and by the misc interrupt handler for responses. It depends on PF response behavior from `cptpf_mbox.c`.

Risks and test signals: risks include polling shared ACK flags without locks or completions, fixed 10 ms sleep granularity, ambiguous error logging labels, and possible stale ACK if interrupts are delayed around consecutive messages. Test signals include PF READY returning VF ID, group binding returning SE/AE type, timeout behavior when PF is absent, and orderly VF_DOWN on remove.
