# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ipsec.c

## Purpose

`ixgbe_ipsec.c` implements ixgbe hardware IPsec crypto offload for the Linux XFRM stack and a restricted SR-IOV mailbox path. It programs device security association tables, starts/stops the security engines, rebuilds tables after reset, translates Tx/Rx data-path metadata, and exposes `xfrmdev_ops` for SA add/delete. The supported algorithm is AES-GCM RFC4106 with 128-bit ICV and a 128-bit key plus optional 32-bit salt.

## Important APIs and Functions

Low-level register writers are `ixgbe_ipsec_set_tx_sa()`, `ixgbe_ipsec_set_rx_item()`, `ixgbe_ipsec_set_rx_sa()`, and `ixgbe_ipsec_set_rx_ip()`. They load key/salt/SPI/IP/mode registers and trigger writes through `IXGBE_IPSTXIDX` or `IXGBE_IPSRXIDX`. Engine lifecycle helpers are `ixgbe_ipsec_clear_hw_tables()`, `ixgbe_ipsec_stop_data()`, `ixgbe_ipsec_stop_engine()`, and `ixgbe_ipsec_start_engine()`.

Public driver hooks are `ixgbe_ipsec_restore()`, `ixgbe_ipsec_vf_clear()`, `ixgbe_ipsec_vf_add_sa()`, `ixgbe_ipsec_vf_del_sa()`, `ixgbe_ipsec_tx()`, `ixgbe_ipsec_rx()`, `ixgbe_init_ipsec_offload()`, and `ixgbe_stop_ipsec_offload()`. XFRM integration is through static `ixgbe_xfrmdev_ops`, where `.xdo_dev_state_add` is `ixgbe_ipsec_add_sa()` and `.xdo_dev_state_delete` is `ixgbe_ipsec_del_sa()`.

## Control Flow

Initialization rejects 82598 and devices whose security engines report offload disabled. It allocates `struct ixgbe_ipsec`, Rx/Tx SA arrays of 1024 entries each, an Rx IP table of 128 entries, initializes the Rx SA hash, stops/clears hardware tables, and assigns `netdev->xfrmdev_ops`.

SA add validates ESP/AH transport-mode crypto offload, checks management/BMC IP filter conflicts, parses AES-GCM key material, allocates a free SA index, and programs software and hardware tables. Rx SAs also allocate or share an Rx IP table entry with reference counting, set mode bits for valid/ESP/decrypt/IPv6, and insert into an RCU hash by SPI for receive lookup. Tx SAs are blocked when VFs exist outside VEPA bridge mode, then programmed into the Tx table. The first SA starts the security engine and sets `IXGBE_FLAG2_IPSEC_ENABLED`.

SA delete derives the hardware index from `xs->xso.offload_handle`, zeros the matching hardware entry, removes Rx entries from the RCU hash, decrements Rx IP references, clears software state, and stops the engine when both SA counts reach zero. Restore after reset stops and clears the engine, restarts it, reloads PF-owned SAs and IP entries, and deletes VF-owned SAs because VF reset or VF-count changes require the VF to request them again.

Tx path `ixgbe_ipsec_tx()` obtains the XFRM state from the skb secpath, validates the offload handle, marks `IXGBE_TX_FLAGS_IPSEC | IXGBE_TX_FLAGS_CC`, fills context descriptor flags for ESP/IP version/encryption, and computes ESP trailer length for non-GSO packets. Rx path `ixgbe_ipsec_rx()` decodes descriptor packet type, locates IPv4/IPv6 and AH/ESP headers, finds the matching Rx state with RCU lookup, attaches a secpath, marks crypto done/success, and increments `adapter->rx_ipsec`.

VF add/delete translate mailbox messages. Add requires a trusted VF and `IXGBE_FLAG2_VF_IPSEC_ENABLED`, currently permits only inbound offload, creates a synthetic `xfrm_state`, calls the regular add path, marks the resulting SA as VF-owned, and returns the PF offload handle. Delete validates ownership before calling the common delete path and frees the synthetic state.

## State and Persistence Behavior

All IPsec offload state is volatile. Hardware SA/IP tables are register-backed and must be reloaded after reset from `adapter->ipsec` software tables. The software state stores XFRM state pointers, keys, salt, mode bits, VF ownership, counts, and Rx IP table references. VF-created `xfrm_state` objects are allocated by the PF and freed on VF delete; PF-owned XFRM states are held by the networking stack. There is no persistence across driver unload. Sensitive key buffers are freed with `kfree_sensitive()` on VF setup failures, but normal table teardown uses plain `kfree()` for allocated arrays whose entries may contain keys.

## Dependencies and Integration Points

This file depends on `net/xfrm.h`, AEAD algorithm descriptors, bridge mode, ixgbe register definitions, descriptor packet-type bits, mailbox opcodes, ethtool private flag `IXGBE_FLAG2_VF_IPSEC_ENABLED`, and Tx descriptor construction in `ixgbe_main.c`/`ixgbe_lib.c`. `ixgbe_main.c` calls Rx and Tx hooks in packet paths, calls restore during reset, and initializes/stops offload during probe/remove. `ixgbe_sriov.c` invokes VF add/delete/clear handlers.

## Risks and Test Signals

Important risks are SA index bounds from untrusted mailbox handles, RCU lifetime around Rx hash deletion, key endianness, management IP filter conflict logic, ESP trailer parsing near skb tail, engine stop waits when link is down, and hardware/software table divergence across resets. VF paths are especially sensitive because synthetic XFRM states and ownership checks must prevent one VF deleting another VF's SA. Tests should cover PF inbound/outbound ESP offload, unsupported algorithms/modes/types, Rx IP table sharing and exhaustion, SA add/delete races with traffic, reset restore, VF trust and private-flag gating, malformed mailbox indices, GSO and non-GSO Tx trailer behavior, Rx AH/ESP descriptor decode, and module unload after active SAs.
