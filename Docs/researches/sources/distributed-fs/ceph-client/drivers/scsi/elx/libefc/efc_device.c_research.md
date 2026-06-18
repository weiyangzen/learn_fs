# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_device.c

## Purpose
`efc_device.c` implements the remote device node state machine for ordinary FC peer devices. It handles PLOGI/PRLI/LOGO/ADISC interactions, node attach, FCP enablement, backend SCSI session notifications, and orderly shutdown/relogin behavior.

## Important APIs, Types, And Functions
Externally declared state handlers include `__efc_d_init`, `__efc_d_wait_plogi_rsp`, `__efc_d_wait_node_attach`, `__efc_d_port_logged_in`, `__efc_d_device_ready`, `__efc_d_device_gone`, and the shutdown/wait states. Helper APIs include `efc_node_init_device`, `efc_process_prli_payload`, `efc_d_send_prli_rsp`, and `efc_send_ls_acc_after_attach`.

## Control Flow And State
New or discovered peers enter `__efc_d_init`. Initiator-capable ports may send PLOGI; target-side PLOGI reception saves service parameters, defers LS_ACC until RPI registration, and waits for domain/topology if needed. Once the node is attached, pending PLOGI or PRLI accepts are sent and the machine advances to port logged-in/device-ready. PRLI payloads set `node->init`/`node->targ`; backend callbacks via `scsi_new_node` and session registration drive `NODE_SESS_REG_OK/FAIL`. Ready nodes enable FCP and react to repeated PLOGI by implicit logout/re-attach, LOGO by explicit shutdown, RSCN missing by `device_gone`, and ADISC by revalidation.

## Dependencies And Integration Points
The file depends on ELS send helpers, domain/topology state from `efc_fabric.c`, hardware node attach/detach commands, `libefc_function_template` SCSI callbacks, and common node cleanup in `efc_node.c`.

## Risks And Test Signals
Risks include ordering races between sent PLOGI completions and incoming PRLI/PLOGI, LS_ACC state stored in `send_ls_acc`/`ls_acc_oxid`, backend async delete/session callbacks, and FCP gating. Several comments note possible ordering problems. Test signals should cover initiator-only, target-only, and I+T logins; PLOGI while ready; LOGO during attach; PRLI before PLOGI response; backend async registration failure; RSCN missing/refound; and shutdown with outstanding ELS and SCSI I/O.
