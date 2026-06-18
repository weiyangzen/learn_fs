<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect-provider.h -->
# sources/distributed-fs/ceph-client/include/linux/interconnect-provider.h

Purpose: Defines provider-side interconnect topology objects, aggregation callbacks, registration APIs, and disabled-config stubs.

Important APIs/types/functions: `icc_units_to_bps()` converts ICC units to Bps. `struct icc_node_data`, `icc_onecell_data`, `icc_provider`, and `icc_node` model phandle translation, one-cell data, provider callbacks, users, inter-provider behavior, topology links, traversal state, request lists, and aggregated/init bandwidth. APIs create/destroy/link/add/delete nodes, remove provider nodes, initialize/register/deregister providers, aggregate standard bandwidth, translate OF phandles, and sync state.

Control flow: Provider drivers create nodes, link topology, register provider callbacks, then consumer requests are aggregated and passed to provider `set()` callbacks.

State/persistence: Provider and node lists persist while registered; node request lists and aggregated bandwidth change with active consumers.

Dependencies/integration: Depends on interconnect consumer API, device tree phandles, device model, lists, hlist, and `CONFIG_INTERCONNECT`.

Risks: Disabled stubs return mixed `-ENOTSUPP`/`-EOPNOTSUPP`; topology cycles or bad links can break path search.

Test signals: Provider registration, OF translation, path requests across linked nodes, aggregation math, sync_state, deregistration cleanup, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect-provider.h -->
