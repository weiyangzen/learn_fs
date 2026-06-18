# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_mbox.c

## Purpose
This file implements PF-side mailbox routing. It handles VF requests locally or forwards them to AF, processes AF responses for PF and VFs, supports PF-up messages for CPT instruction LMTST, and configures inline IPsec LFs requested by other RVU components.

## Important APIs and functions
Public handlers are `otx2_cptpf_vfpf_mbox_intr()`, `otx2_cptpf_vfpf_mbox_handler()`, `otx2_cptpf_afpf_mbox_intr()`, `otx2_cptpf_afpf_mbox_handler()`, and `otx2_cptpf_afpf_mbox_up_handler()`. Inline LF APIs exported through the PF header are `otx2_inline_cptlf_setup()` and `otx2_inline_cptlf_cleanup()`. Local handlers include `handle_msg_get_caps()`, `handle_msg_get_eng_grp_num()`, `handle_msg_kvf_limits()`, `handle_msg_rx_inline_ipsec_lf_cfg()`, `rx_inline_ipsec_lf_cfg()`, and `forward_to_af()`/`forward_to_vf()`.

## Control flow
VF mailbox interrupts identify the VF bit, queue its work item, clear the interrupt, then workqueue code reads all VF messages. Known PF-serviced messages return capabilities, engine group numbers, kernel VF LF limits, or inline IPsec LF configuration. Unknown valid VF messages are copied into the AF mailbox under `cptpf->lock`. AF response handling validates signatures, routes messages with VF pcifuncs back to VF mailbox memory, and processes PF responses locally to update PF id, LF MSI-X offsets, register read results, and attach/detach flags. AF-up `CPT_INST_LMTST` messages submit one instruction through the inline LF if configured.

## State and persistence
This file mutates `cptpf->pf_id`, LF MSI-X offsets, LF attach flags, inline LF state for CPT0/CPT1, VF mailbox response buffers, and capability responses. Inline LF setup attaches one high-priority LF per block and configures NIX/CPT inline IPsec via AF mailbox. No persistent storage is used.

## Dependencies and integration points
It depends on PF state from `otx2_cptpf.h`, mailbox helpers, LF lifecycle, engine-group lookup, RVU pcifunc helpers, and NIX/CPT mailbox message definitions. It is the integration point between VF driver requests and AF resource control.

## Risks and edge cases
Message size copying must preserve mailbox headers correctly; malformed signatures are rejected. `forward_to_af()` treats only `-EIO` as AF communication failure and forwards other AF result codes later. Inline IPsec setup must unwind CPT1 and CPT0 LFs if NIX/CPT configuration fails. AF response routing ignores `MBOX_MSG_VF_FLR` to VFs. The VF interrupt loop iterates two banks and must not schedule beyond `enabled_vfs`.

## Test signals
Test signals include VF capability and engine group mailbox exchanges, AF register read/write responses updating caller storage, invalid signature rejection, inline IPsec LF config and cleanup, AF-up LMTST command handling, VF counts above 64, and mailbox timeout/failure injection with no stuck mutex.
