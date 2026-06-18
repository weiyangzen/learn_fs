# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_vf.c

## Purpose
Implements VF-specific fm10k hardware operations and mailbox handlers. It discovers VF queue resources assigned by the PF, resets/stops VF queues, retrieves PF-provided MAC/VLAN/ITR information, requests VLAN/MAC/multicast/xcast/logical-port changes through the PF mailbox, and exposes a VF `fm10k_info` operation table.

## Important APIs, Types, and Functions
Externally used handlers and data are `fm10k_mac_vlan_msg_attr`, `fm10k_msg_mac_vlan_vf`, `fm10k_lport_state_msg_attr`, `fm10k_msg_lport_state_vf`, and `fm10k_vf_info`. Core internal functions are `fm10k_stop_hw_vf`, `fm10k_reset_hw_vf`, `fm10k_init_hw_vf`, `fm10k_update_vlan_vf`, `fm10k_read_mac_addr_vf`, `fm10k_update_uc_addr_vf`, `fm10k_update_mc_addr_vf`, `fm10k_update_int_moderator_vf`, `fm10k_update_lport_state_vf`, `fm10k_update_xcast_mode_vf`, `fm10k_update_hw_stats_vf`, and `fm10k_rebind_hw_stats_vf`. `mac_ops_vf` wires these into generic fm10k code.

## Control Flow
VF init first verifies queue 0 is assigned, probes additional queues by checking descriptor cache offsets and queue ownership, disables the owned queues, records `max_queues`, reads the default VLAN from `TXQCTL(0)`, and reads the PF-provided ITR scale from the software-defined TDLEN bits. Stop disables queues through generic code, restores the permanent MAC and ITR scale into queue base/TDLEN registers for a future VF init, and returns pending-request status if relevant. Reset stops hardware, sets `VFCTRL_RST`, waits, clears the bit, and verifies reset completion. MAC/VLAN operations build `FM10K_VF_MSG_ID_MAC_VLAN` TLVs and enqueue them to the PF mailbox. Logical-port enable resets local DGLORT state, sends an LPORT_STATE request, and waits for a ready indication; disable includes the DISABLE bool. Xcast and MSI-X updates are mailbox requests to the PF.

## State and Persistence Behavior
VF state is held in `hw->mac.perm_addr`, `hw->mac.addr`, `hw->mac.default_vid`, `hw->mac.vlan_override`, `hw->mac.max_queues`, `hw->mac.itr_scale`, and `hw->mac.dglort_map`. The PF persists some VF bootstrap data in queue base registers and TDLEN until the VF reads it. Mailbox replies can update permanent MAC/default VLAN and LPORT readiness. Stats are queue-only and use generic queue-stat helpers over `max_queues`.

## Dependencies and Integration Points
Includes `fm10k_vf.h`, which brings in the common and type contracts. It depends on generic fm10k queue stop/start/stats helpers, TLV helpers, PF/VF mailbox initialization through `fm10k_pfvf_mbx_init`, Linux bitfield helpers, Ethernet address validation, and mailbox `enqueue_tx`. It integrates with the PF implementation through shared VF message IDs and attributes.

## Risks
VF initialization relies on PF-programmed register encodings, including the TDLEN ITR-scale handoff and MAC storage in queue base registers. Queue discovery uses inverted register reads to detect unavailable or PF-owned queues, so hardware semantics must not change. VF unicast changes enforce a locked permanent MAC when one exists; changing that can weaken PF policy. Mailbox sends mostly return enqueue status but do not wait for policy acceptance. `fm10k_configure_dglort_map_vf` is a stub, so callers must not expect local DGLORT programming on VFs.

## Test Signals
VF probe/init with one and multiple queues, no-resource detection, queue disable pending behavior, VF reset bit completion, PF-provided MAC/default VLAN/vlan-override mailbox update, MAC read from base registers, locked-MAC rejection, VLAN set/clear with reserved-bit rejection, multicast validation, MSI-X rescan requests, LPORT enable/disable ready state, xcast mode requests, stats update/rebind, and PF absent or mailbox enqueue failure paths should be covered.
