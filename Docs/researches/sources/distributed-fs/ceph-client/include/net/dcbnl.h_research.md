# sources/distributed-fs/ceph-client/include/net/dcbnl.h

Read `sources/distributed-fs/ceph-client/include/net/dcbnl.h` completely for this pass (136 lines, 5104 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dcbnl.h_research.md`.

Purpose: declares the kernel-side DCB netlink helper API and driver operation table for IEEE 802.1Qaz, CEE DCBX, app priority mappings, rewrite mappings, buffer configuration, apptrust, and notifications.

Important APIs/types/functions: `struct dcb_app_type` stores ifindex, `struct dcb_app`, list node, and DCBX mode. Helper APIs include rewrite operations `dcb_getrewr/setrewr/delrewr`, app table operations `dcb_setapp/getapp`, IEEE app operations `dcb_ieee_setapp/delapp/getapp_mask`, map extractors for PCP/DSCP priority and rewrite masks, `dcb_ieee_getapp_default_prio_mask()`, and notify functions `dcbnl_ieee_notify()` and `dcbnl_cee_notify()`. `struct dcbnl_rtnl_ops` is the large per-netdevice callback table for ETS, maxrate, QCN, PFC, app tables, CEE PG/PFC, capabilities, DCBX mode, peer app data, buffers, apptrust, and rewrite add/delete.

Control flow: userspace sends DCB netlink requests; dcbnl core validates and dispatches to a netdevice's `dcbnl_rtnl_ops`, updates shared app/rewrite tables through helpers, then notifies listeners. Drivers implement only supported callbacks. App priority map helpers summarize table state into masks indexed by TC or DSCP.

State and persistence: DCB app/rewrite state is runtime per netdevice/ifindex state. Driver callbacks may reflect hardware or firmware state for ETS/PFC/DCBX/buffers. The header defines contracts; persistent storage, if any, is device-specific.

Dependencies and integration points: depends on `linux/dcbnl.h`, netdevices, DCB netlink families, IEEE 802.1Qaz/CEE data structures, DCBX, and driver ethtool/netlink control paths.

Risks: callback support is sparse and drivers must return consistent errors for unsupported operations. Priority masks and selectors for DSCP/PCP/apptrust are easy to misinterpret. Shared app tables must remain synchronized with hardware DCBX state. Notifications need correct event/cmd/seq/pid values to keep userspace consistent.

Test signals: dcbtool/iproute2 DCB operations for ETS/PFC/app tables, rewrite add/delete, DSCP/PCP map extraction, apptrust setting, buffer settings, peer CEE/IEEE reads, DCBX mode changes, notification observation, and driver unsupported-callback behavior.
