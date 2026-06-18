# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/filter.h

## Purpose

`filter.h` defines the generic hardware filter specification contract used by the Solarflare driver. It gives common code and hardware-specific backends a shared representation for RX/TX filters, match fields, priorities, flags, encapsulation types, queue targets, RSS behavior, VLANs, MAC addresses, IP addresses, and ports.

The file also provides inline initializers and setters that keep callers from manually assembling inconsistent `struct efx_filter_spec` values.

## Important APIs, Types, and Functions

Core enums are `efx_filter_match_flags` for match dimensions, `efx_filter_priority` for replacement policy, `efx_filter_flags` for RX/TX behavior, and `efx_encap_type` for none/VXLAN/NVGRE/GENEVE plus an IPv6 outer-frame flag. `struct efx_filter_spec` is the main logical filter description, holding match flags, priority, flags, DMA queue ID, RSS context user ID, VLAN IDs, local/remote MACs, EtherType, protocol, local/remote hosts, ports, and encapsulation type.

Constants include `EFX_FILTER_RX_DMAQ_ID_DROP` for RX drop filters and `EFX_FILTER_VID_UNSPEC` for unspecified VLAN matches.

Inline helpers include `efx_filter_init_rx()`, `efx_filter_init_tx()`, `efx_filter_set_ipv4_local()`, `efx_filter_set_ipv4_full()`, `efx_filter_set_eth_local()`, `efx_filter_set_uc_def()`, `efx_filter_set_mc_def()`, `efx_filter_set_encap_type()`, and `efx_filter_get_encap_type()`.

## Control Flow

Normal caller flow is to initialize a spec with `efx_filter_init_rx()` or `efx_filter_init_tx()`, add match dimensions with setters, then pass it to a NIC-specific insertion operation such as the Falcon/Siena implementation in `farch.c`. The setters are additive and OR match flags while filling corresponding fields. `efx_filter_set_eth_local()` rejects the empty case where both VID and address are unspecified.

## State and Persistence Behavior

`filter.h` owns no global state. Each `efx_filter_spec` is caller-owned stack or heap data. Persistence is handled by hardware-specific code that stores accepted specs in per-NIC filter tables and replays them after reset. In this subset, `farch.c` converts these generic specs into `efx_farch_filter_spec` entries under `efx->filter_state`.

## Dependencies and Integration Points

The header depends on Linux types, Ethernet address definitions, byte-order helpers, `htons()`, and `ether_addr_copy()`. It is consumed by receive mode programming, ethtool/NFC-like filter management, accelerated RFS, SR-IOV/user-level networking paths, and NIC-specific backends. The comments document hardware capability differences across Falcon, Siena, and later hardware.

## Risks and Edge Cases

Callers must initialize specs with the provided init functions. `match_flags` combinations are not universally supported, so backends may reject legal-looking specs. `rss_context` zero means the default driver RSS context, not necessarily a firmware context ID. `EFX_FILTER_FLAG_RX_OVER_AUTO` is backend-owned and affects auto-filter restoration. The struct can represent IPv6 and encapsulated filters even though Falcon/Siena accepts a narrower subset here.

## Test Signals

Useful tests include initializer zeroing checks, setter field/match flag checks, rejection of empty Ethernet-local filters, round-trip conversion through hardware-specific get operations, priority replacement behavior in the backend, RX RSS/scatter flag propagation, default unicast/multicast filter behavior, and stable errors for unsupported match combinations.
