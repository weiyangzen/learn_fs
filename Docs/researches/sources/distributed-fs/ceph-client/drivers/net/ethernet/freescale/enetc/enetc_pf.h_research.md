# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pf.h

## Purpose
Defines PF-private data structures, constants, operation hooks, and mailbox prototypes shared by rev1 and rev4 PF implementation files.

## Important APIs, Types, and Functions
Key types are `enum enetc_vf_flags`, `struct enetc_vf_state`, `struct enetc_port_caps`, `struct enetc_pf_ops`, and `struct enetc_pf`. It declares `enetc_msg_psi_init`, `enetc_msg_psi_free`, and `enetc_msg_handle_rxmsg`. The `phylink_to_enetc_pf` helper maps a phylink config back to its PF container.

## Control Flow
The header has no runtime control flow except macro expansion. It supplies function-pointer dispatch for generation-specific MAC address access, PCS creation/destruction, and optional PSFP enablement.

## State and Persistence
`struct enetc_pf` stores the PF's SI pointer, VF counts and flags, software MAC filter entries, VF mailbox buffers/work item, VLAN promiscuity/hash/active VLAN bitmaps, external/internal MDIO buses, PCS, PHY interface mode, phylink config, hardware capabilities, PF ops table, and ENETC4 MAFT entry count.

## Dependencies and Integration Points
Includes `enetc.h` and phylink. Consumed by `enetc_pf.c`, `enetc4_pf.c`, `enetc_msg.c`, MDIO helpers, and PF common helpers. Its fields bridge netdev, PCI SR-IOV, phylink, mailbox, VLAN, and hardware-filter code.

## Risks
As shared private ABI, field semantics must remain consistent across rev1 and rev4. Some fields are generation-specific (`num_mfe`, capabilities, `enable_psfp`) and callers must guard them. Bitmap sizes and `ENETC_MAX_NUM_VFS` bound mailbox/filter arrays.

## Test Signals
Compile both rev1 and rev4 PFs, SR-IOV-enabled and disabled builds, PSFP-capable and non-PSFP configs, and verify probe/remove paths initialize only the fields each generation later uses.
