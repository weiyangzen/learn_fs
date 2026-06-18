# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_filters.h

## Purpose
`mcdi_filters.h` declares the firmware-backed filter/RSS interface and the software state structures used by `mcdi_filters.c`. It bridges generic SFC filter operations to MCDI-managed filter tables.

## Important APIs And Types
`enum efx_mcdi_filter_default_filters` names per-VLAN automatic default filters for broadcast, unicast/multicast default traffic, and VXLAN/NVGRE/GENEVE IPv4/IPv6 unicast/multicast defaults. `struct efx_mcdi_filter_vlan` stores a VLAN ID plus automatic unicast, multicast, and default filter IDs. `struct efx_mcdi_filter_table` stores supported firmware match masks, RSS-context mode, the software hash table and firmware handles, address-list shadows, promiscuous/overflow state, restore flags, multicast chaining support, VLAN-filtering state, and the VLAN list.

Exports cover table probe/down/remove/restore, MC allocation reset, match support checks, RX mode sync, safe filter insert/remove/get/count/clear/list, VLAN add/find/delete/cleanup, RSS context push/pull/free/restore, default indirection programming, no-op RX scatter update, and optional RFS expiry.

## Control Flow Role
The header is used by NIC type code, netdevice receive-mode paths, VLAN paths, ethtool RSS operations, and RFS code. Probe must run under the filter semaphore write lock. Many APIs take locks internally, while VLAN find/delete and table removal rely on documented caller locking.

## State And Persistence Behavior
All declared structures are RAM shadows of firmware resources. Firmware handles and RSS context IDs are runtime allocations; saved specs, VLAN arrays, and restore flags are used to rebuild firmware state after MC reboot. There is no disk persistence.

## Dependencies And Integration Points
The header depends on `net_driver.h`, `filter.h`, and `mcdi_pcol.h`. It integrates with `efx->filter_state`, `efx->filter_sem`, RSS context storage, netdev features/address lists, VLAN offload, RFS acceleration, and the core MCDI API.

## Risks And Edge Cases
`EFX_MCDI_FILTER_TBL_ROWS` and filter ID encoding are tightly coupled to insertion, lookup, removal, and userspace-visible IDs. Address-list limits determine when the implementation falls back to promiscuous/all-multicast behavior. The header's locking comments must be followed by callers because the implementation can otherwise leak or race table state.

## Test Signals
Build with RFS enabled and disabled. Runtime tests should verify ID limits, VLAN filter initialization to invalid IDs, table restoration flags after MC reset, and RX mode sync behavior at unicast/multicast list limits.
