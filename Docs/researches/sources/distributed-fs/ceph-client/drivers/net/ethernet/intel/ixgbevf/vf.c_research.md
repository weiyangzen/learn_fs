# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/vf.c

## Purpose
`vf.c` implements the hardware abstraction operations for ixgbe virtual functions. It translates driver requests into VF register operations and PF mailbox commands, with separate Hyper-V variants for environments where PF/VF communication is exposed differently.

## Important APIs, Types, and Functions
- Operation tables: `ixgbevf_mac_ops`, `ixgbevf_hv_mac_ops`, and exported `ixgbevf_info` instances per VF device family.
- Reset/init/stop/link: `ixgbevf_reset_hw_vf()`, `ixgbevf_hv_reset_hw_vf()`, `ixgbevf_init_hw_vf()`, `ixgbevf_stop_hw_vf()`, `ixgbevf_check_mac_link_vf()`, Hyper-V link checks, and `ixgbe_read_vflinks()`.
- PF-mediated configuration: set RAR/UC/multicast/VLAN/LPE/xcast mode, API negotiation, feature negotiation, PF link query, queue query, RETA query, and RSS key query.
- Public locked helpers: `ixgbevf_get_queues()`, `ixgbevf_get_reta_locked()`, and `ixgbevf_get_rss_key_locked()`.

## Control Flow
Reset stops adapter queues, resets API version and mailbox ops to legacy, writes `VFCTRL.RST`, waits for reset indication to clear, sends `IXGBE_VF_RESET`, polls for permanent MAC/multicast filter type, and updates `perm_addr`. API negotiation tries versions in the caller and stores the accepted version. Later mailbox functions construct command buffers, call write-then-read helper, clear `CTS`, and validate success/failure bits before updating outputs.

Link checking either asks E610/API 1.6+ PF for link state or reads `VFLINKS`, then verifies PF clear-to-send by reading the mailbox. Hyper-V variants avoid mailbox operations and mostly return `-EOPNOTSUPP`, except reset reads permanent MAC from PCI config space and RLPML writes Rx control directly.

## State and Persistence Behavior
This file mutates `hw->adapter_stopped`, `hw->api_version`, `hw->mac.addr`, `perm_addr`, `mc_filter_type`, queue maxima, `get_link_status`, and `hw->mbx` ops/timeouts. PF-accepted settings such as MAC, VLAN, multicast, xcast, link, and feature support persist in PF/VF device state.

## Dependencies and Integration Points
It depends on the mailbox transport, VF register macros, netdev multicast iteration, PCI config access for Hyper-V, and local driver structures. `ixgbevf_main.c` calls these ops under `mbx_lock` when changing netdev state or reconfiguring queues. API version gates must align with `mbx.h` command definitions and PF support.

## Risks and Edge Cases
- Reset may accept PF failure for unassigned MAC but leaves caller to assign random MAC.
- API-specific helpers return `-EOPNOTSUPP` for unsupported device/API combinations; callers must degrade cleanly.
- RETA/RSS key mailbox layout assumes 82599/X540 compression and a max of two queues in current driver use.
- Multicast programming truncates to 30 non-link-local entries.
- `ixgbevf_check_mac_link_vf()` sets `*link_up = !get_link_status`, so mailbox error paths can intentionally defer link-down reporting.

## Test Signals
Test PF reset in progress, successful and failed VF reset replies, API negotiation fallback, Hyper-V board IDs, VLAN/MAC/multicast/xcast permission failures, E610 PF link query, VFLINKS speed decode, queue query validation, RETA/RSS key permission and unsupported paths, and PF feature negotiation for IPsec/ESX mailbox.
