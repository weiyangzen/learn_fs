# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/vf.c

## Purpose
`vf.c` implements VF-specific MAC operations and PF-mediated configuration commands. It initializes operation tables, resets the VF, obtains permanent MAC address information from the PF, reports link state, and requests MAC, multicast, unicast, VLAN, and maximum packet length changes through the mailbox.

## Important APIs, Types, And Functions
The public entry points are `e1000_init_function_pointers_vf()` and `e1000_rlpml_set_vf()`. Internal callbacks installed into `hw->mac.ops` include `e1000_reset_hw_vf()`, `e1000_init_hw_vf()`, `e1000_check_for_link_vf()`, `e1000_get_link_up_info_vf()`, `e1000_update_mc_addr_list_vf()`, `e1000_rar_set_vf()`, `e1000_read_mac_addr_vf()`, `e1000_set_uc_addr_vf()`, and `e1000_set_vfta_vf()`.

## Control Flow
Software initialization installs MAC and mailbox init callbacks. Reset asserts `CTRL.RST`, waits for PF reset indications to clear, enables mailbox timeout, sends `E1000_VF_RESET`, and reads the PF response containing the permanent MAC address or a NACK. MAC/VLAN/multicast/LPE changes build mailbox command buffers, send them with posted writes, and parse ACK/NACK responses. Link checks notice PF reset or mailbox timeout, read hardware `STATUS.LU`, consume PF CTS messages, and may request a driver reset if communication needs reinitialization.

## State And Persistence
Hardware identity and operations live in `struct e1000_hw`. MAC state includes `addr`, `perm_addr`, type, RAR count, MTA count, and `get_link_status`. Mailbox timeout state determines whether PF communication is considered live. The permanent MAC persists in `hw->mac.perm_addr` after PF reset response.

## Dependencies And Integration Points
The file uses mailbox ops from `mbx.c`, register macros from `regs.h`, constants from `mbx.h`/`defines.h`, and kernel Ethernet address helpers. `netdev.c` calls these operations under `hw->mbx_lock` for reset, filter programming, VLAN restore, MTU/LPE changes, and link watchdog checks.

## Risks
Most configuration is at PF discretion, so NACKs and timeouts must be handled gracefully. Multicast programming truncates to 30 hashes due to mailbox size. Link status can be stale because the VF cannot read PHY state directly. MAC filter additions can fail with `ENOSPC`. Reset sequencing depends on PF responsiveness and the mailbox timeout being restored only after reset.

## Test Signals
Validate PF-assigned MAC address, random fallback when missing, VF MAC changes accepted/rejected by PF, VLAN add/remove NACK handling, multicast filter programming, LPE updates on MTU changes, link up/down reporting, and behavior during PF reset or PF driver unload.
