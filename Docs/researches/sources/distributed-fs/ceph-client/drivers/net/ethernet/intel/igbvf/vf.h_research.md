# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/vf.h

## Purpose
`vf.h` defines the VF hardware abstraction for `igbvf`: supported PCI IDs, advanced RX/TX descriptor layouts, MAC and mailbox operation tables, VF stats layout, hardware state structure, and prototypes shared by `vf.c`, `mbx.c`, and `netdev.c`.

## Important APIs, Types, And Functions
Core definitions include `union e1000_adv_rx_desc`, `union e1000_adv_tx_desc`, `struct e1000_adv_tx_context_desc`, `enum e1000_mac_type`, `struct e1000_vf_stats`, `struct e1000_mac_operations`, `struct e1000_mbx_operations`, `struct e1000_mbx_info`, `struct e1000_dev_spec_vf`, and `struct e1000_hw`. Exported prototypes are `e1000_rlpml_set_vf()` and `e1000_init_function_pointers_vf()`.

## Control Flow
The header does not execute code but enables polymorphic hardware behavior through function pointer tables. `netdev.c` calls `hw->mac.ops.*` without knowing whether the underlying VF is 82576 or I350-style.

## State And Persistence
`struct e1000_hw` stores MMIO pointers, MAC state, mailbox state, device-specific VF mailbox cache, PCI identity fields, and the mailbox spinlock. `struct e1000_vf_stats` stores base, last, and accumulated values for VF counters that do not clear on read.

## Dependencies And Integration Points
The header includes PCI, delay, interrupt, Ethernet, `regs.h`, and `defines.h`, and includes `mbx.h` after core type definitions so mailbox structs can reference `struct e1000_hw`. It is the common hardware contract used by all `igbvf` implementation files.

## Risks
Descriptor layout must match hardware exactly; any packing or field change would break DMA interpretation. Operation pointer contracts require callers to hold the mailbox lock for PF-mediated actions. The included headers form a tight dependency cycle that should be changed cautiously.

## Test Signals
Build and sparse coverage are important. Runtime tests should validate descriptor TX/RX operation, stats rollover accounting, mailbox initialization, and device ID matching for both 82576 VF and I350 VF.
