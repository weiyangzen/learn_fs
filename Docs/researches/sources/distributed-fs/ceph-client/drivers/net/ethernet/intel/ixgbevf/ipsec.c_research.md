# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ipsec.c

## Purpose
`ipsec.c` implements VF-side XFRM/IPsec crypto offload for ixgbevf. The VF validates XFRM states, keeps local RX/TX security-association tables, asks the PF to program or delete real hardware SA entries through mailbox messages, annotates TX descriptors for offload, and marks RX packets as successfully crypto-processed.

## Important APIs, types, and functions
- PF mailbox helpers: `ixgbevf_ipsec_set_pf_sa()` and `ixgbevf_ipsec_del_pf_sa()`.
- SA lifecycle: `ixgbevf_ipsec_add_sa()`, `ixgbevf_ipsec_del_sa()`, `ixgbevf_ipsec_restore()`, and `ixgbevf_ipsec_find_empty_idx()`.
- RX lookup: `ixgbevf_ipsec_find_rx_state()` uses an RCU hash keyed by SPI.
- Key validation: `ixgbevf_ipsec_parse_proto_keys()` accepts only `rfc4106(gcm(aes))` with 128-bit ICV and a supported key/salt layout.
- Data path hooks: `ixgbevf_ipsec_tx()` fills `ixgbevf_ipsec_tx_data` and TX flags, while `ixgbevf_ipsec_rx()` builds secpath/xfrm offload status from RX descriptor packet type bits.
- Initialization/teardown: `ixgbevf_init_ipsec_offload()` and `ixgbevf_stop_ipsec_offload()`.

## Control flow and integration
Initialization checks mailbox API/PF feature support, allocates `struct ixgbevf_ipsec`, RX/TX tables with 1024 entries each, installs `xfrmdev_ops`, and enables ESP-related netdev features. State add validates protocol, transport mode, crypto-offload type, no compression for RX, table capacity, algorithm/key shape, and then requests PF programming. The returned PF SA handle is stored in the local table and exposed through `xs->xso.offload_handle`.

On TX, the driver locates the outbound xfrm state from the SKB, maps the offload handle to the local TX SA table, stores the PF SA index for the context descriptor, sets IPsec/checksum flags, selects ESP/IP version/encryption bits, and computes non-GSO ESP trailer length. On RX, descriptor packet-type bits identify IPv4/IPv6 plus AH/ESP, the SPI and destination address find the matching RX state, and the SKB secpath is marked `CRYPTO_DONE`/`CRYPTO_SUCCESS`.

## State and persistence behavior
State is in `adapter->ipsec`, `rx_tbl`, `tx_tbl`, RX RCU hash table, `num_rx_sa`, `num_tx_sa`, PF SA handles, XFRM offload handles, and adapter counters `tx_ipsec`/`rx_ipsec`. Hardware state persists in the PF-managed SA tables and must be restored after VF reset through `ixgbevf_ipsec_restore()`.

## Dependencies
The file depends on XFRM device offload APIs, crypto AEAD metadata, IP/AH/ESP headers, SKB secpath helpers, ixgbevf mailbox locking and send/poll functions, descriptor flags from `defines.h`, and feature negotiation through `adapter->pf_features`.

## Risks
- `ixgbevf_ipsec_restore()` requests PF reprogramming but does not update stored `pfsa` handles on success, so PF handle stability is assumed across reset.
- RX secpath failure after `xfrm_state_hold()` can leak a reference unless ownership is handled elsewhere.
- SA delete trusts offload handles enough to index tables after subtracting base offsets; corrupted handles can be dangerous.
- The algorithm/key parser is intentionally narrow; unsupported modern algorithms will be rejected.
- Mailbox failures leave local and PF state boundaries sensitive to partial add/delete behavior.

## Test signals
Validate XFRM state add/delete for inbound/outbound ESP and AH, unsupported mode/protocol/algorithm rejection with extack messages, mailbox PF failure paths, reset and restore, TX descriptor flag/context generation including GSO/non-GSO ESP trailer lengths, RX secpath marking for IPv4 and IPv6, and SA table exhaustion.
