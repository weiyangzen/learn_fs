# sources/distributed-fs/ceph-client/include/xen/interface/io/displif.h

Purpose: defines the Xen paravirtual display protocol, a richer display ABI than `fbif` with multiple connectors, dynamically created display buffers, framebuffer attachment, page flips, EDID retrieval, and asynchronous events.

Important APIs/types/functions: protocol version constants, XenStore field names, operations `XENDISPL_OP_DBUF_CREATE`, `DBUF_DESTROY`, `FB_ATTACH`, `FB_DETACH`, `SET_CONFIG`, `PG_FLIP`, and `GET_EDID`; event `XENDISPL_EVT_PG_FLIP`; request structs such as `xendispl_dbuf_create_req`, `xendispl_page_directory`, `xendispl_fb_attach_req`, `xendispl_set_config_req`, `xendispl_get_edid_req`; `xendispl_req`, `xendispl_resp`, `xendispl_evt`, and `struct xendispl_event_page`.

Control flow: XenBus negotiates backend versions, frontend selected version, connector resolution, request rings, event rings, and backend allocation. Requests go through per-connector control rings, with non-connector-specific operations using connector 0. Backends respond with status and may send page-flip completion events through the separate event page.

State and persistence: display buffers and framebuffers are identified by guest-unique cookies and persist until explicit destroy/detach. Shared buffer page directories hold grant refs. Connector configuration and transport keys persist in XenStore.

Dependencies and integration points: includes `ring.h` and `grant_table.h`. Integrates with XenBus state transitions, grant sharing, event channels, DRM/KMS style frontends, and optional EDID consumers.

Risks: cookie value zero is invalid and duplicate cookies are protocol errors. Buffer size determines page directory length; mismatches can expose invalid grants. Recovery flow requires frontends to block new clients while reconfiguring after backend failure.

Test signals: multi-connector setup, buffer create/destroy with frontend and backend allocation, framebuffer attach/detach, config reset/set bounds checks, page-flip event delivery, EDID size handling, and protocol version 1 vs 2 behavior.
