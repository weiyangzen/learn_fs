# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/virtchnl.c

## Purpose
This file is the ICE PF-side virtchnl control plane for SR-IOV VFs. It receives mailbox requests, validates ABI messages, checks VF state and opcode allowlists, dispatches to operation handlers, and sends responses or asynchronous events back to VFs. The covered feature surface includes version/resource negotiation, link and reset notifications, MAC filters, promiscuous mode, VLAN v1/v2 filtering and offloads, RSS delegation, flexible RXDID query, QoS, PTP capability/time, and switchdev representor-specific behavior.

## Important APIs, Types, And Functions
Public functions include `ice_vc_notify_vf_link_state()`, `ice_vc_notify_link_state()`, `ice_vc_notify_reset()`, `ice_vc_send_msg_to_vf()`, `ice_vc_isvalid_vsi_id()`, `ice_vf_ena_vlan_promisc()`, `ice_is_vlan_promisc_allowed()`, `ice_virtchnl_set_dflt_ops()`, `ice_virtchnl_set_repr_ops()`, and `ice_vc_process_vf_msg()`. Static handlers implement each opcode. Two `struct ice_virtchnl_ops` instances, `ice_virtchnl_dflt_ops` and `ice_virtchnl_repr_ops`, provide mode-specific behavior while keeping the dispatcher table stable.

## Control Flow
Mailbox processing starts in `ice_vc_process_vf_msg()`. It extracts opcode, VF id, message pointer, and length from the AQ event, obtains the VF, locks `vf->cfg_lock`, rejects malicious or disabled VFs, validates message shape with `virtchnl_vc_validate_vf_msg()`, checks `ice_vc_is_opcode_allowed()`, then switches by opcode and invokes the selected operation table. `VIRTCHNL_OP_GET_VF_RESOURCES` negotiates `vf->driver_caps`, sets `ICE_VF_STATE_ACTIVE`, initializes VLAN stripping, and sends link state. Other paths validate active state and `ICE_VF_VSI_ID` before touching VSI resources.

## State And Persistence
The file mutates VF runtime state including `vf->vf_ver`, `vf->driver_caps`, `vf->vf_states`, `vf->num_mac`, `vf->dev_lan_addr`, `vf->hw_lan_addr`, `vf->legacy_last_added_umac`, VLAN capability cache `vf->vlan_v2_caps`, VLAN strip flags, promiscuous state bits, PTP capability bits, and mailbox maliciousness state. MAC hardware address behavior is intentionally persistent across VF reboot in `hw_lan_addr`, while `dev_lan_addr` can be cleared and repopulated. Hardware filter, VLAN, RSS, scheduler, interrupt, and PTP state is applied through ICE subsystem helpers.

## Dependencies And Integration Points
The dispatcher integrates with the admin queue mailbox, virtchnl ABI, VF library, queues, RSS, Flow Director, VLAN ops, filter programming, DCB/QoS, flex pipe RXDID, PTP, and switchdev representor mode. It sends all VF responses through `ice_aq_send_msg_to_vf()` via `ice_vc_send_msg_to_vf()`. Queue and FDIR handlers are declared outside this file and connected through `ice_virtchnl_ops`.

## Risks
This is a large security boundary: untrusted VFs can submit mailbox messages. Risks include missed capability checks, allowing untrusted MAC/LLDP/promiscuous/VLAN actions, stale allowlist state after capability negotiation, inconsistent SVM/DVM VLAN handling, failure to restore VLAN filtering after deletes, and races around VF removal if `cfg_lock` or reference handling is bypassed. The representor ops intentionally do not program firmware MAC filters, so default and switchdev behavior must stay aligned where required.

## Test Signals
High-value tests exercise full VF init ordering, invalid message validation, disabled and malicious VF paths, link/reset event broadcasts, admin-set MAC restrictions, legacy MAC add-before-delete ordering, untrusted LLDP rejection, trusted and untrusted MAC/VLAN limits, SVM and DVM VLAN v1/v2 capability matrices, VLAN stripping/insertion toggles with CRC strip disabled, RSS opcode dispatch, QoS capability responses, PTP caps/time responses, representor MAC/promisc behavior, and default unsupported-opcode responses.
