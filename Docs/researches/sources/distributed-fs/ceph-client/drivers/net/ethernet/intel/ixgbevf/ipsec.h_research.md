# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ipsec.h

## Purpose
`ipsec.h` defines ixgbevf's IPsec offload data model shared between the VF header, IPsec implementation, and TX/RX data paths.

## Important APIs, types, and constants
- Capacity and index bases: 1024 SAs, RX base 0, TX base 1024.
- Authentication and RX mode bits: 128-bit auth, valid, ESP, decrypt, and IPv6 flags.
- `struct rx_sa`, `struct tx_sa`, and `struct rx_ip_sa` describe local SA metadata.
- `struct ixgbevf_ipsec_tx_data` carries descriptor-time TX offload flags, trailer length, and PF SA index.
- `struct ixgbevf_ipsec` owns RX/TX table pointers, table counts, and the RX hash table.
- `struct sa_mbx_msg` is the compact VF-to-PF mailbox payload for SA programming.

## Control flow and integration
The header is included by `ixgbevf.h`; when `CONFIG_IXGBEVF_IPSEC` is enabled, data path prototypes use these structures. `ipsec.c` allocates and fills the table structures and casts mailbox buffers to `struct sa_mbx_msg` when communicating with the PF.

## State and persistence behavior
The structures hold XFRM state pointers, keys, salt, address, mode bits, PF SA handles, local usage flags, and RCU hash nodes. This is volatile driver state; PF hardware SA state is represented by `pfsa` handles and restored after VF reset.

## Dependencies
It depends on kernel hash-list types, XFRM state declarations through includers, endian integer types, and mailbox size/layout agreement with PF code.

## Risks
Mailbox layout changes must remain synchronized with PF expectations. Key material is stored in kernel memory tables until teardown/delete, so zeroing and lifetime handling matter. The local table capacity and base-index arithmetic must match `ipsec.c`.

## Test signals
Build with IPsec enabled, add/delete enough SAs to exercise RX/TX index bases and table limits, validate mailbox payloads for IPv4/IPv6, and check reset restore preserves expected PF SA handles.
