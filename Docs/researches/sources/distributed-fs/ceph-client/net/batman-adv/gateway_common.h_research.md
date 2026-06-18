<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.h research

Purpose: exposes common gateway declarations and user-visible gateway mode names. It is the small shared header between mesh initialization, sysfs/netlink settings code, and gateway client logic.

Important APIs and types: defines `enum batadv_bandwidth_units` with kbit and mbit units, string constants for OFF, CLIENT, and SERVER gateway modes, and prototypes for TVLV container update, gateway init, and gateway free.

Control flow and state behavior: no state is stored here. The mode name constants must remain aligned with user-facing configuration parsing elsewhere. `batadv_gw_init()` and `batadv_gw_free()` are lifecycle hooks called from mesh init/free.

Dependencies and integration: includes `main.h` for `struct batadv_priv`. The declarations connect gateway mode configuration, TVLV advertisement, and gateway client tracking.

Risks: changing string constants can break userspace configuration expectations. Bandwidth unit enum changes must stay aligned with parsers/formatters outside this file.

Test signals: build gateway configuration code, test parsing/display of gateway mode names, and verify init/free lifecycle remains paired during mesh interface creation/destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.h -->
