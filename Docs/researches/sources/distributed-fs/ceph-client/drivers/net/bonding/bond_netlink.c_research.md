# sources/distributed-fs/ceph-client/drivers/net/bonding/bond_netlink.c

## Purpose
`bond_netlink.c` exposes bonding through rtnetlink's `RTM_NEWLINK`/`RTM_SETLINK` link-kind interface. It defines the netlink attribute policy for bond masters and bond slaves, translates netlink attributes into shared bonding option changes, serializes current bond and slave state back into netlink messages, provides 802.3ad extended stats, and registers the `struct rtnl_link_ops` named `"bond"`.

## Important APIs, Types, and Functions
- `bond_policy[]` validates master attributes from `IFLA_BOND_*`, including mode, active slave, MII/ARP monitoring, targets, primary selection, failover MAC, hash policy, peer notifications, min links, ALB/TLB/802.3ad options, IPv6 NS targets, coupled control, and broadcast neighbour settings. `IFLA_BOND_PEER_NOTIF_DELAY` uses a range policy capped at 300000 ms.
- `bond_slave_policy[]` validates per-slave attributes: queue ID, slave priority, and 802.3ad actor port priority.
- `bond_validate()` validates the generic `IFLA_ADDRESS` attribute for correct Ethernet length and a valid unicast MAC.
- `bond_changelink()` is the master configuration path. It walks each supplied `IFLA_BOND_*` attribute, initializes a `struct bond_opt_value`, and calls `__bond_opt_set()` with the original nlattr and extack for shared validation and side effects.
- `bond_slave_changelink()` is the per-slave configuration path for queue ID, priority, and actor port priority. It converts queue ID to the legacy `slave_name:queue_id` string expected by the option implementation, and uses slave-aware option values for priority fields.
- `bond_newlink()` registers a newly allocated bond netdevice, forces carrier off, initializes work items, and applies initial netlink attributes through `bond_changelink()`, rolling back registration and work on failure.
- `bond_get_size()` and `bond_fill_info()` provide master netlink dump sizing and serialization. They report current configured values, active/primary ifindexes, nested ARP and IPv6 NS targets, optional 802.3ad actor fields for privileged callers, and active aggregator info.
- `bond_get_slave_size()` and `bond_fill_slave_info()` provide per-slave dump sizing and serialization, including state, MII status, link failures, permanent MAC, queue ID, priority, and 802.3ad port/aggregator/churn details when applicable.
- `bond_get_linkxstats_size()` and `bond_fill_linkxstats()` expose nested `LINK_XSTATS_TYPE_BOND` and `BOND_XSTATS_3AD` stats for master or slave xstats requests.
- `bond_netlink_init()` and `bond_netlink_fini()` register and unregister `bond_link_ops`.

## Control Flow
During module initialization, `bonding_init()` in `bond_main.c` calls `bond_netlink_init()`, which registers `bond_link_ops` with rtnetlink. After that, user space can create bonds with `ip link add type bond ...`; rtnetlink allocates the netdevice using `bond_link_ops.priv_size` and `.setup = bond_setup`, then calls `bond_newlink()`. `bond_newlink()` registers the netdevice, marks carrier off, initializes delayed work, and invokes `bond_changelink()` to apply any creation attributes. If configuration fails, it cancels work and unregisters the netdevice.

For later master updates, rtnetlink calls `bond_changelink()`. The function treats every present nlattr as a requested option update and applies them sequentially. It handles special prechecks that are specific to netlink shape: active and primary slave attributes arrive as ifindexes and are resolved to names for the option layer; `use_carrier` is accepted only as `1` because disabling it is obsolete; ARP interval and ARP validate reject simultaneous MII monitoring using the local `miimon` value observed earlier in the same message; ARP and IPv6 target nests clear the existing target arrays before replaying nested entries; actor system length is checked before passing the value through.

For per-slave updates, rtnetlink calls `bond_slave_changelink()` with the master and lower device. Queue ID, priority, and actor port priority are converted into the option layer's accepted value forms and applied through `__bond_opt_set()`. Errors return immediately so later attributes are not applied after a failed update.

For dumps, rtnetlink first asks sizing functions, then calls fill functions. `bond_fill_info()` serializes simple scalar parameters, conditionally emits active and primary ifindexes, emits nested ARP/NS target lists only when non-empty, and, in 802.3ad mode, emits actor configuration for `CAP_NET_ADMIN` callers and current aggregator information when available. `bond_fill_slave_info()` obtains the `struct slave` from the lower device under RTNL and emits generic slave state, then enters an RCU section to safely read the 802.3ad aggregator pointer before appending aggregator and port-state attributes.

## State and Persistence
This file owns no long-lived mutable bonding state beyond the static rtnetlink policies and `bond_link_ops`. All persistent runtime state lives in `struct bonding`, `struct slave`, 802.3ad state, and shared option data owned by other bonding files. Netlink updates mutate `bond->params`, active/primary slave pointers, target arrays, per-slave fields, and mode-specific state through `__bond_opt_set()` rather than direct assignment.

The serialization paths are snapshot-style. They read live fields under RTNL, RCU, or helper functions; no state is cached between netlink requests. Netlink message size calculations must stay synchronized with fill functions because underruns surface as `-EMSGSIZE`.

## Dependencies and Integration Points
`bond_netlink.c` depends on Linux netlink/rtnetlink APIs (`nla_policy`, `nla_put_*`, nested attributes, `rtnl_link_ops`, extack messages), netdevice helpers, IPv6 address helpers, and bonding internals from `net/bonding.h` and `net/bond_3ad.h`. Its main integration point is the shared option engine in `bond_options.c`: every mutating attribute is delegated to `__bond_opt_set()` so sysfs, ioctl, module parameters, and netlink follow common validation and side-effect rules.

It also integrates with `bond_main.c` for creation (`bond_setup`, `bond_work_init_all`, `bond_get_num_tx_queues`), with 802.3ad helpers for active aggregator info and stats, with per-slave sysfs-visible state through `struct slave`, and with rtnetlink xstats for extended LACP counters.

## Risks
Sequential option application means a multi-attribute netlink change can partially apply earlier attributes before a later one fails; callers must rely on the option layer and extack to understand failure points. The ARP interval versus MII check uses a local `miimon` variable initialized to zero and updated only if the same message includes `IFLA_BOND_MIIMON`, so the shared option layer remains critical for rejecting conflicts against existing state. ARP/NS target replacement clears existing targets before replaying nested values, so a malformed later target can leave earlier changes applied unless option-layer rollback is provided elsewhere.

Dump sizing is manually mirrored against serialization. Adding a new attribute requires updating policy, change handling, size calculation, fill handling, and often option definitions. 802.3ad slave info reads an RCU aggregator pointer while using RTNL-derived slave state; missing or changing aggregators are handled by omitting optional fields, but tests should cover no-aggregator states. `IFLA_BOND_AD_ACTOR_SYSTEM` is treated as `NLA_BINARY` of `ETH_ALEN`, but the setter path converts with `nla_get_u64()`, so byte ordering and length assumptions are worth regression coverage.

## Test Signals
Test signals include successful `ip link add ... type bond` creation with initial attributes, rollback when initial attributes fail, `ip link set ... type bond` updates for every supported `IFLA_BOND_*` attribute, and extack messages for invalid address, disabled `use_carrier`, bad target lengths, nonexistent active slave ifindex, and monitor conflicts. Per-slave tests should update queue ID, priority, and actor port priority and confirm netlink dumps reflect the changes.

Dump tests should verify `bond_get_size()`/`bond_fill_info()` and slave sizing/fill paths do not return `-EMSGSIZE`, nested ARP and IPv6 NS target attributes appear only when configured, active and primary slaves are emitted as ifindexes, privileged 802.3ad actor fields are gated by `CAP_NET_ADMIN`, and aggregator info is omitted gracefully when unavailable. Xstats tests should cover master and slave 802.3ad stats, unsupported xstats attrs returning zero or `-EINVAL` as appropriate, and module unload calling `bond_netlink_fini()` after notifier unregister in `bonding_exit()`.
