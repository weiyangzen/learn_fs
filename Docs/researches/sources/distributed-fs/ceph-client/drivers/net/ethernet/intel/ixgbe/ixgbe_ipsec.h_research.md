# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ipsec.h

## Purpose

`ixgbe_ipsec.h` defines the table sizes, register command bit encodings, and software state structures used by ixgbe IPsec offload. It is the shared contract between `ixgbe_ipsec.c`, `ixgbe.h`, and packet/virtualization paths that need `struct ixgbe_ipsec_tx_data` or mailbox SA message layouts.

## Important Types and Constants

`IXGBE_IPSEC_MAX_SA_COUNT` sets 1024 entries for each Rx and Tx SA table. `IXGBE_IPSEC_MAX_RX_IP_COUNT` sets the separate 128-entry destination IP table used by Rx lookup. `IXGBE_IPSEC_BASE_RX_INDEX` and `IXGBE_IPSEC_BASE_TX_INDEX` partition XFRM offload handles so Rx handles start at 0 and Tx handles start at 1024. `IXGBE_IPSEC_AUTH_BITS` fixes 128-bit authentication.

`IXGBE_RXTXIDX_*`, `enum ixgbe_ipsec_tbl_sel`, and `IXGBE_RXMOD_*` encode table selection, read/write commands, valid/decrypt/protocol/IP-version bits, and VF ownership mode bits used when programming security registers. `struct rx_sa` stores an inbound SA, including hash node, XFRM state, destination IP, key, salt, hardware mode, Rx IP table index, decrypt flag, and VF owner. `struct rx_ip_sa` stores one shared destination IP entry and reference count. `struct tx_sa` stores outbound XFRM state, key/salt/mode/encrypt/owner fields. `struct ixgbe_ipsec_tx_data` is the per-packet data passed from `ixgbe_ipsec_tx()` into context descriptor setup. `struct ixgbe_ipsec` owns all software tables and the Rx SA hash. `struct sa_mbx_msg` is the PF/VF mailbox payload for SA add/delete translation.

## Control Flow and Integration Points

The header has no executable control flow. Its structures drive `ixgbe_init_ipsec_offload()` allocation, XFRM SA add/delete, VF mailbox operations in `ixgbe_sriov.c`, and Tx context descriptor construction in `ixgbe_main.c`. The offload handle base constants are part of the implicit ABI between XFRM state setup, Tx/Rx data paths, and mailbox responses.

## State and Persistence Behavior

The declared tables are runtime-only mirrors of device hardware tables. `used` flags and counters are the authoritative software allocation state, while hardware programming happens separately. Keys and salts are stored in memory inside allocated table arrays. `rx_ip_sa.ref_cnt` allows multiple Rx SAs to share one destination IP table entry.

## Dependencies, Risks, and Test Signals

The header depends on XFRM types, hlist/hash support, endian address types, and ixgbe register definitions included through the parent include graph. Risks are mostly contract risks: changing table sizes or handle bases breaks handle decoding; changing `sa_mbx_msg` breaks PF/VF mailbox compatibility; changing mode bits can program the wrong hardware table behavior. Tests should include compile coverage with and without `CONFIG_IXGBE_IPSEC`, SA handle boundary tests around 1023/1024, Rx IP reference-count tests, and VF mailbox compatibility checks.
