# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_pfvf_mbox.c

## Purpose
This file implements the PF side of the PF/VF mailbox protocol. It services VF requests for mailbox version negotiation, link status, Rx/link state, MTU, MAC address, firmware info, offload configuration, bulk link/stats reads, and VF removal, and it forwards PF-originated notifications such as link-status changes to VFs.

## Important APIs, Types, And Functions
- Version gating: `pfvf_cmd_versions[]` maps opcodes to the minimum mailbox version and `octep_pfvf_validate_version()` negotiates the effective version per VF.
- Command handlers: `octep_pfvf_set_mtu()`, `octep_pfvf_get_mtu()`, `octep_pfvf_set_mac_addr()`, `octep_pfvf_get_mac_addr()`, `octep_pfvf_set_rx_state()`, `octep_pfvf_set_link_status()`, `octep_pfvf_get_link_status()`, `octep_pfvf_get_fw_info()`, `octep_pfvf_set_offloads()`, and `octep_pfvf_dev_remove()`.
- Bulk reads: `octep_pfvf_pf_get_data()` stages `octep_iface_link_info` or combined Rx/Tx stats into `mbox->config_data` and returns six-byte fragments on follow-up reads.
- Lifecycle: `octep_setup_pfvf_mbox()` allocates one mailbox object per active VF at the VF's first ring, initializes work, mutexes, register pointers, and VF info; `octep_delete_pfvf_mbox()` cancels and frees those mailboxes.
- Work entry: `octep_pfvf_mbox_work()` reads the VF command register, dispatches by opcode, and writes the response word back.

## Control Flow
PF setup uses active VF count and rings-per-VF from configuration, allocates `struct octep_mbox` at `vf_id * rings_per_vf`, and asks chip-specific `setup_mbox_regs()` to bind PF-to-VF and VF-to-PF data registers. A hardware mailbox interrupt schedules `octep_pfvf_mbox_work()`. The worker serializes the mailbox with `mbox->lock`, reads the command from `vf_pf_data_reg`, handles it, and writes the response to the same VF/PF data register.

Most command handlers proxy the VF request to firmware through `octep_ctrl_net_*()` APIs with the VF ID. MAC handling has extra PF policy: if PF has administratively set the VF MAC, VF attempts to set its own MAC are NACKed and GET returns the PF-maintained address. Bulk link-info and stats reads start with an ACK carrying total byte length, then VF issues fragment requests and PF copies up to `OCTEP_PFVF_MBOX_MAX_DATA_SIZE` bytes per response.

Notifications flow in the opposite direction. `octep_pfvf_notify()` decodes firmware-to-host control mailbox messages, builds a PF/VF mailbox notification word, checks negotiated VF mailbox version in `octep_send_notification()`, and writes the notification to the PF-to-VF data register under the mailbox mutex.

## State And Persistence
Runtime state lives in `oct->mbox[]`, `oct->vf_info[]`, and each mailbox's fragment buffer fields: `config_data_index`, `message_len`, and `config_data`. `vf_info[vf_id].mbox_version` stores negotiation result; `vf_info[vf_id].mac_addr` and flags store PF-managed VF MAC policy. No disk persistence exists. Firmware state may be changed through control mailbox calls for link, Rx, MTU, MAC, remove, and offloads.

## Dependencies And Integration Points
The file depends on `octep_main.h` for device and mailbox structures, `octep_pfvf_mbox.h` for protocol layout, and `octep_ctrl_net.h` for firmware commands. It is integrated with chip-specific interrupt handlers that schedule mailbox work, PF netdev SR-IOV code that sets active VFs, and control mailbox notification delivery from firmware.

## Risks And Edge Cases
- The mailbox protocol fits responses into one 64-bit word, so bulk data fragmentation must maintain index and length accurately.
- Version gating is only applied to PF-originated notifications in this file; command dispatch assumes VF behavior is compatible after negotiation.
- `MAX_VF_PF_MBOX_DATA_SIZE` must cover the largest staged link/stats payload; mismatches can overflow or truncate if structures grow.
- Setup allocates only active VFs present at setup time. If active VFs change after probe, mailbox allocation policy must stay consistent with SR-IOV enable flow.
- Teardown must cancel pending work before freeing mailbox memory.

## Test Signals
Test by loading PF with SR-IOV enabled, probing VFs, validating mailbox version negotiation, VF MAC/MTU/offload/link operations, PF-administered VF MAC rejection, bulk `GET_LINK_INFO` and `GET_STATS` responses over multiple fragments, PF link-status notification delivery, VF remove notification to firmware, and clean unload while mailbox work may be pending.
