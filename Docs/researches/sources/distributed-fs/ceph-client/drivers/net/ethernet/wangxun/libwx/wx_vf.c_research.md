# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf.c

## Purpose
`wx_vf.c` implements shared VF-side low-level hardware and PF mailbox operations. It resets a VF, stops VF queues, negotiates mailbox API version, requests MAC/VLAN/multicast/MACVLAN/LPE/link/FW/queue configuration from the PF, and derives link status from PF notifications or VF status registers.

## Important APIs, Types, and Functions
Exports include `wx_init_hw_vf()`, `wx_reset_hw_vf()`, `wx_stop_adapter_vf()`, `wx_set_rar_vf()`, `wx_update_mc_addr_list_vf()`, `wx_update_xcast_mode_vf()`, `wx_get_link_state_vf()`, `wx_set_vfta_vf()`, `wx_get_mac_addr_vf()`, `wx_get_fw_version_vf()`, `wx_set_uc_addr_vf()`, `wx_rlpml_set_vf()`, `wx_negotiate_api_version()`, `wx_get_queues_vf()`, and `wx_check_mac_link_vf()`. Internal helpers perform posted mailbox write/read and VF register clearing.

## Control Flow
Reset starts by stopping queues and masking interrupts, backing up MSI-X vector state from `b4_addr` when available, asserting `WX_VXCTRL_RST`, waiting for reset completion, restoring vector state, enabling AML BME if needed, clearing VF RX descriptor controls, enabling mailbox timeouts, then sending `WX_VF_RESET` to the PF. The PF response either supplies the permanent MAC or nacks when no administrator-assigned MAC exists.

Configuration APIs format mailbox commands and either post fire-and-forget requests or wait for PF replies. Link checking first consumes PF mailbox notifications (`WX_PF_NOFITY_VF_LINK_STATUS` or `WX_PF_CONTROL_MSG`), then falls back to polling `WX_VXSTATUS` and translating speed bits through `wx_speed_lookup_vf`.

## State and Persistence Behavior
Runtime state includes `wx->mac.addr`, `wx->mac.perm_addr`, `wx->mac.mc_filter_type`, VF API level in `wx->vfinfo->vf_api`, mailbox timeout, link/speed/notify flags, and queue limits returned by the PF. Hardware register state is reset and reprogrammed across VF reset/open; no state is persisted to disk.

## Dependencies and Integration Points
The file depends on VF register macros from `wx_vf.h`, mailbox routines from `wx_mbx.h`, common hardware helpers, `struct wx` from `wx_type.h`, netdev multicast lists, and Linux PCI/MMIO primitives. It is consumed by `wx_vf_common.c` and concrete VF drivers such as `ngbevf`.

## Risks and Edge Cases
Mailbox APIs assume the PF honors API 1.3 semantics for xcast and queue queries; older PFs return errors. `wx_update_mc_addr_list_vf()` caps multicast hashes at 28 despite `WX_MAX_VF_MC_ENTRIES` being 30. Reset depends on the PF being up and able to answer; timeout returns `-EBUSY`. Link status can be stale if PF notifications are missed and hardware status polling races module link transitions.

## Test Signals
Test VF probe with PF up/down, no assigned MAC, random MAC fallback, mailbox API negotiation failure, queue count validation, multicast overflow, VLAN add/remove ack/nack, UC filter list clear/add, xcast mode on old API, and link notifications for up/down/notify-down. Reset tests should verify MSI-X vector save/restore and AML BME programming.
