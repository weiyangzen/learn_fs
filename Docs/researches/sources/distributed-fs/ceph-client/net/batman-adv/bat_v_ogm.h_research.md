# sources/distributed-fs/ceph-client/net/batman-adv/bat_v_ogm.h

## Purpose
`bat_v_ogm.h` declares the BATMAN V OGMv2 APIs shared between `bat_v.c`, `bat_v_elp.c`, and the OGMv2 implementation.

## Important APIs
- Mesh lifecycle: `batadv_v_ogm_init`, `batadv_v_ogm_free`.
- Interface/aggregation lifecycle: `batadv_v_ogm_aggr_work`, `batadv_v_ogm_iface_enable`, `batadv_v_ogm_iface_disable`.
- Originator helper: `batadv_v_ogm_orig_get`, used by ELP and OGMv2 receive paths.
- Primary-interface update: `batadv_v_ogm_primary_iface_set`.
- Packet receive: `batadv_v_ogm_packet_recv`.

## Control Flow and Integration
`bat_v.c` calls lifecycle and primary hooks; `bat_v_elp.c` calls originator creation when an ELP names a peer originator; packet registration uses `batadv_v_ogm_packet_recv` for `BATADV_OGM2`.

## State and Persistence
No header-local state. Declared functions mutate per-mesh OGMv2 state, per-interface aggregation state, and originator tables.

## Risks and Test Signals
Risks are declaration/implementation drift and misuse of originator helper without reference release. Test signals include BATMAN V mesh init/free, ELP neighbor creation, OGM2 receive handler registration, and teardown with aggregation work canceled.
