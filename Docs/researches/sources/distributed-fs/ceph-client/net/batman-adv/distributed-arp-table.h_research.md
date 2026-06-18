<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/distributed-arp-table.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/distributed-arp-table.h research

Purpose: declares DAT integration points and compile-time stubs. It lets routing, bridge, TT, netlink, and DHCP gateway paths call DAT code without scattering `#ifdef CONFIG_BATMAN_ADV_DAT` throughout the codebase.

Important APIs and types: when enabled it defines `BATADV_DAT_ADDR_MAX`, ARP/DHCP snooping prototypes, `batadv_dat_drop_broadcast_packet()`, init/free, status update, netlink dump, and `batadv_dat_inc_counter()`. Inline helpers `batadv_dat_init_orig_node_addr()` and `batadv_dat_init_own_addr()` derive DAT ring addresses from originator or primary interface MAC addresses using `batadv_choose_orig()`.

Control flow and state behavior: the header itself stores no state. Enabled inline address initialization mutates `orig_node->dat_addr` and `bat_priv->dat.addr`. Disabled stubs return false for snoopers/drop decisions, no-op status and address initialization, return success for init, and `-EOPNOTSUPP` for netlink cache dumps.

Dependencies and integration: includes `main.h`, `originator.h`, netdevice/netlink/skbuff types, and batman packet UAPI types. The header directly exposes DAT counters for received unicast 4addr subtypes and keeps ethtool statistics updates close to packet receive code.

Risks: callers must understand ownership semantics of boolean returns: several enabled functions free or consume skbs on true, while disabled stubs never do. Address initialization depends on a valid primary interface. Counter helper silently ignores non-DAT subtypes.

Test signals: build all DAT on/off combinations, ensure no unresolved references in disabled builds, verify address hashes are assigned after primary interface changes, validate `batadv_dat_inc_counter()` increments GET/PUT RX counters only, and verify netlink DAT cache dump is unsupported when DAT is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/distributed-arp-table.h -->
