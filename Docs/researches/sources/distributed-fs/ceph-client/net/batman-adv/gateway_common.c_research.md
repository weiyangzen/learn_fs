<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.c research

Purpose: implements gateway TVLV advertisement and reception common to gateway server/client modes. It registers the gateway TVLV handler, publishes local server bandwidth when needed, and translates incoming TVLVs into gateway node updates.

Important APIs and functions: public functions are `batadv_gw_tvlv_container_update()`, `batadv_gw_init()`, and `batadv_gw_free()`. Internal `batadv_gw_tvlv_ogm_handler_v1()` parses incoming gateway TVLV values or absence notifications.

Control flow: container update reads `bat_priv->gw.mode`. OFF and CLIENT unregister the local gateway TVLV; SERVER reads atomic down/up bandwidth, converts to network order, and registers a `BATADV_TVLV_GW` version 1 container. The OGM handler treats CIFNOTFND or too-short values as zero bandwidth, sanitizes zero down/up values as removal, calls `batadv_gw_node_update()`, and requests election in client mode when a nonzero gateway is seen. Init initializes selection class through `algo_ops->gw.init_sel_class()` when available or defaults to 1, then registers the OGM handler with CIFNOTFND. Free unregisters local container and handler.

State and persistence: this file stores no own state, but mutates TVLV containers and gateway node state under `bat_priv->gw`. Gateway advertisements reflect current atomic mode/bandwidth values and are regenerated when settings change.

Dependencies and integration: depends on TVLV registration, gateway client node/election functions, atomic gateway settings, and batman packet gateway TVLV structures. It is called from mesh init/free and from settings code that changes gateway mode or bandwidth.

Risks: malformed or short TVLVs must always remove capability, not retain stale gateway nodes. Zero bandwidth is treated as gateway removal. Client election is only triggered on nonzero announcements, so removal paths rely on `batadv_gw_node_update()` to mark reselection if needed.

Test signals: switch gateway mode off/client/server, bandwidth zero/nonzero, receive valid/short/missing gateway TVLVs, verify TVLV registration/unregistration, and confirm client mode election is triggered on new viable gateway announcements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_common.c -->
