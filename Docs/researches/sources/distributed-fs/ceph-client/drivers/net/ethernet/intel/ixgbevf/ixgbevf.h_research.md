# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ixgbevf.h

## Purpose
`ixgbevf.h` is the central private header for the ixgbe VF driver. It defines ring buffers, queue vectors, adapter state, descriptor helpers, queue limits, XDP/IPsec integration points, feature flags, state bits, and cross-file function prototypes.

## Important APIs, types, and functions
- Ring data structures: `ixgbevf_tx_buffer`, `ixgbevf_rx_buffer`, `ixgbevf_ring`, `ixgbevf_ring_container`, and `ixgbevf_q_vector`.
- Adapter root object: `struct ixgbevf_adapter` contains queue arrays, XDP rings, netdev/PCI/hardware pointers, mailbox lock, stats, service work/timer, RSS state, flags, and optional IPsec state.
- Ring state helpers: XDP ring flags, large-buffer/build-skb flags, TX hang flags, descriptor unused calculation, descriptor address macros, and tail write helper.
- Constants: queue counts, descriptor bounds/defaults, RSS sizes, RX buffer sizes, interrupt throttle values, jumbo frame size, DMA attributes, and TX flag bits.
- Cross-file prototypes: open/close/up/down/reset, resource setup/free, stats update, ethtool ops install, EITR write, mailbox poll/write, and IPsec hooks or stubs.

## Control flow and integration
Most ixgbevf source files include this header and operate through the structures defined here. The main driver allocates and owns `struct ixgbevf_adapter`; ethtool mutates ring counts and flags; data path code advances ring indices and uses descriptor macros; mailbox code serializes PF communication through `mbx_lock`; optional IPsec hooks compile to no-op stubs when disabled.

## State and persistence behavior
The adapter structure is the runtime persistence root for the VF lifetime. It stores queue topology, ring descriptor memory and DMA addresses, interrupt moderation settings, netdev state, hardware state, PF feature negotiation, RSS configuration, service state bits, link status, XDP program/rings, and optional IPsec tables. Ring state persists across NAPI polls and is reset or rebuilt by resource setup/teardown and interface reset flows.

## Dependencies
The header depends on Linux netdevice, timer, IO, VLAN, u64 stats, XDP, bit operations, and ixgbevf hardware headers `vf.h` and `ipsec.h`. It must stay aligned with descriptor definitions in `defines.h` and implementation assumptions in `ixgbevf_main.c`, `ethtool.c`, `mbx.c`, and `ipsec.c`.

## Risks
- Layout changes to `ixgbevf_adapter` can affect code relying on the first field being `active_vlans`.
- Queue array bounds are fixed and must match PF-negotiated queue counts.
- Descriptor helper arithmetic assumes ring indices are maintained correctly and one descriptor remains unused.
- Optional IPsec stubs must match real prototypes exactly to keep non-IPsec builds safe.
- XDP, RSS, and interrupt fields are shared across reset, ethtool, and data path code, making locking/state-bit discipline important.

## Test signals
Full driver build with and without `CONFIG_IXGBEVF_IPSEC`, probe/remove, interface reset, RX/TX traffic, XDP attach/detach, ethtool ring/stat/coalesce operations, RSS queries, mailbox feature negotiation, TX hang detection, and IPsec-enabled builds all validate this header's contracts.
