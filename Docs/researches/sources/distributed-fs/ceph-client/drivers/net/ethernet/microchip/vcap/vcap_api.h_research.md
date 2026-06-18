# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api.h

## Purpose
`vcap_api.h` defines the core model, rule, admin, cache, command, and callback contracts shared by VCAP API clients and the implementation. It is the foundational header that maps generated VCAP model metadata to runtime rule administration.

## Important APIs, Types, and Constants
The chain constants (`VCAP_CID_*`, `VCAP_CID_LOOKUP_SIZE`) define reserved chain-id ranges for ingress, prerouting, stage 2, and egress lookups. `enum vcap_user` orders known rule owners and is used in rule sort keys. `struct vcap_field`, `struct vcap_set`, `struct vcap_typegroup`, and `struct vcap_info` describe generated key/action field layouts, keysets/actionsets, typegroup bits, and per-VCAP dimensions. `struct vcap_cache_data` defines the hardware cache staging streams.

`struct vcap_admin` is the per-instance runtime state: admin list linkage, rule and enabled-port lists, mutex, VCAP type/instance identifiers, chain range, target instance, lookup counts, valid address range, `last_used_addr`, word-ordering flag, traffic direction, and cache. `struct vcap_rule` is the client-visible rule with chain id, user, priority, id, cookie, key/action lists, selected keyset/actionset, extended error, and client scratch value.

`struct vcap_operations` is the hardware/platform callback table. `struct vcap_control` binds callbacks, model metadata, stats/name tables, and the admin list.

## Control Flow and Integration
The header does not implement behavior, but it defines the state consumed by `vcap_api.c`, debugfs, and platform drivers such as Microchip switch drivers. Clients allocate rules, fill `keyfields` and `actionfields`, and call client APIs; the implementation validates against `vcaps`, stages data in `vcap_cache_data`, and delegates actual hardware access to `vcap_operations`.

## State and Persistence Behavior
The runtime state declared here is long-lived driver memory. Rule lists and enabled-port lists are protected by `vcap_admin.lock`; hardware persistence is abstracted through cache/update/init/move callbacks. `last_used_addr` and valid address bounds are critical for persistent hardware layout across rule additions and deletions.

## Dependencies
The header depends on Linux `types`, `list`, `netdevice`, and the generated model header `vcap_ag_api.h`. It intentionally avoids including debugfs or KUnit specifics.

## Risks and Test Signals
The main risk is contract drift between generated model arrays and enum/index usage. Misconfigured `sw_width`, `act_width`, typegroup maps, or callback tables will break encoding at runtime. KUnit tests use this header extensively through mocked `struct vcap_control`, `struct vcap_admin`, and cache streams.
