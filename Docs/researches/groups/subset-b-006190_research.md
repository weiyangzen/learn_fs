# subset-b-006190 Research

Grouped code research for devlink trap handling, managed netdev helpers, DNS resolver key/upcall support, and the DSA core files in this work item. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/trap.c -->
# sources/distributed-fs/ceph-client/net/devlink/trap.c

## Purpose
This file implements devlink packet trap, trap group, and trap policer registration plus their generic netlink control and notification paths. It is the common devlink layer that lets switch/NIC drivers expose packets trapped to the CPU, configure drop-trap actions, associate trap groups with policers, report trap statistics, and feed drop monitor tracepoints.

## Important APIs, Types, And Functions
Internal objects wrap immutable driver-provided descriptors with runtime state:

- `struct devlink_trap_item`: descriptor, group pointer, mutable action, per-CPU stats, and driver private pointer.
- `struct devlink_trap_group_item`: descriptor, optional policer association, list node, and per-CPU group stats.
- `struct devlink_trap_policer_item`: descriptor plus mutable rate and burst.
- `struct devlink_stats`: per-CPU RX packet/byte counters protected by `u64_stats_sync`.

The exported registration API is `devl_traps_register()`, `devlink_traps_register()`, `devl_traps_unregister()`, `devlink_traps_unregister()`, `devl_trap_groups_register()`, `devlink_trap_groups_register()`, `devl_trap_groups_unregister()`, `devlink_trap_groups_unregister()`, `devl_trap_policers_register()`, and `devl_trap_policers_unregister()`. Runtime packet reporting is exported through `devlink_trap_report()`, and drivers recover their private cookie through `devlink_trap_ctx_priv()`.

Netlink handlers include `devlink_nl_trap_get_doit()`, `devlink_nl_trap_get_dumpit()`, `devlink_nl_trap_set_doit()`, group get/dump/set variants, and policer get/dump/set variants. Fill helpers serialize names, generic flags, action, type, metadata capabilities, stats, policer IDs, rate, and burst into devlink netlink attributes.

## Control Flow
Drivers register policers first if groups reference them, then groups, then traps. Verification distinguishes generic descriptors, whose IDs/names/types must match devlink's built-in tables, from driver-specific descriptors, whose IDs must sit outside the generic range and whose names must not collide with generic traps or groups.

Trap registration allocates a `devlink_trap_item`, per-CPU stats, links it to its initial group by ID, invokes `devlink->ops->trap_init()`, adds it to `devlink->trap_list`, and sends a `DEVLINK_CMD_TRAP_NEW` notification if the devlink is registered and listeners exist. Unregistration disables traps to drop, waits for RCU grace with `synchronize_rcu()`, then removes items in reverse order and calls optional driver fini hooks.

Netlink get/dump paths look up list entries and serialize state. Set paths validate action values, call driver callbacks, update cached state, and report extack errors. Group action setting either uses a driver group callback or falls back to per-trap action setting; group policer changes validate the policer ID and call `trap_group_set()`. Policer set validates rate/burst against min/max before calling `trap_policer_set()` and updating cached values.

When a driver reports a packet, `devlink_trap_report()` updates per-trap and per-group stats on the current CPU and emits the `devlink_trap_report` tracepoint with metadata derived from the trap item, group, input devlink port, and optional flow-action cookie.

## State And Persistence
All state is in memory under the owning `struct devlink`: `trap_list`, `trap_group_list`, and `trap_policer_list`. Mutable action, policer attachment, rate, burst, and counters persist only for the lifetime of the devlink instance and registered objects. Per-CPU stats are monotonically accumulated until unregistration frees them.

## Dependencies And Integration Points
The file depends on `devl_internal.h`, generic netlink devlink helpers, `trace/events/devlink.h`, `netdev_alloc_pcpu_stats()`, `u64_stats`, RCU synchronization, and driver callbacks in `struct devlink_ops`: trap init/fini/action, group init/set/action, policer init/fini/set/counter, and drop counters. Userspace integration is through devlink generic netlink commands and asynchronous notifications.

## Risks And Edge Cases
Group action setting may partially commit changes when per-trap fallback succeeds for earlier traps and later traps fail; the extack text explicitly warns about committed changes. Non-drop traps silently skip action changes when their current action differs, because only drop traps are action-mutable. Registration ordering matters: traps require groups to exist, and groups may require policers to exist. Statistics reads aggregate all possible CPUs and can be stale relative to concurrent reports, though `u64_stats_sync` avoids torn 64-bit values.

## Test Signals
Useful tests are devlink selftests or driver tests that register generic and driver traps, verify duplicate/name/ID rejection, perform netlink get/dump/set operations, change group actions and policers, check extack messages for invalid inputs, report packets, and validate per-trap/group counters plus drop monitor tracepoint emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/trap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devres.c -->
# sources/distributed-fs/ceph-client/net/devres.c

## Purpose
This small file provides devres-managed helpers for network devices. It lets drivers allocate Ethernet `struct net_device` instances and register them so cleanup is tied to the lifetime of a parent `struct device`.

## Important APIs, Types, And Functions
`struct net_device_devres` stores the managed `struct net_device *`. `devm_alloc_etherdev_mqs()` wraps `alloc_etherdev_mqs()`, records the resulting device in devres, and exports the helper. `devm_register_netdev()` validates that the netdev was already allocated through the same device's devres, registers it with `register_netdev()`, and adds a second devres action that calls `unregister_netdev()`. `netdev_devres_match()` is the matcher used to prove the same netdev is managed.

## Control Flow
Allocation first allocates a devres record, then allocates the Ethernet netdev, then adds the record to the managing device. Registration refuses unmanaged netdevs with `WARN_ON()` and `-EINVAL`, allocates an unregister devres record, calls `register_netdev()`, and only after success installs the unregister action on `ndev->dev.parent`.

## State And Persistence
The state is a pair of devres records: one freeing the netdev and one unregistering it. Ordering is controlled by devres release order during device detach; the netdev exists until the managed free action runs.

## Dependencies And Integration Points
This integrates with the Linux driver-core devres mechanism, `<linux/etherdevice.h>`, and normal netdev registration. It is intended for device drivers whose netdev allocation and registration should unwind automatically when the parent device goes away.

## Risks And Edge Cases
`devm_register_netdev()` requires the netdev to be managed by the same device and currently assumes the only managed allocator is `devm_alloc_etherdev_mqs()`. Passing a netdev allocated elsewhere returns `-EINVAL`. The unregister devres record is added to `ndev->dev.parent`, so parent assignment must be correct by registration time.

## Test Signals
Tests should cover successful managed allocation/registration, registration failure cleanup, rejection of unmanaged netdevs, and detach-time ordering that unregisters before freeing the netdev.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dns_resolver/Kconfig -->
# sources/distributed-fs/ceph-client/net/dns_resolver/Kconfig

## Purpose
This Kconfig file defines the `DNS_RESOLVER` tristate option for the kernel DNS resolver key type.

## Important APIs, Types, And Functions
The single option is `config DNS_RESOLVER`, labelled "DNS Resolver support". It depends on `KEYS`, can be built in or as module `dns_resolver`, and documents the userspace request-key upcall helper.

## Control Flow
When selected, the build includes `net/dns_resolver/` and enables DNS lookup upcalls through the kernel key retention service. Consumers such as CIFS and AFS can request keys of type `dns_resolver`.

## State And Persistence
The Kconfig option has no runtime state. It controls whether the module/key type exists in the kernel build.

## Dependencies And Integration Points
The explicit dependency is `KEYS`; practical integration is with `/sbin/dns.resolver`, `/etc/request-key.conf`, CIFS, AFS, and `Documentation/networking/dns_resolver.rst`.

## Risks And Edge Cases
Enabling this without a matching userspace helper means DNS lookups fail at runtime despite the kernel type existing. If built as a module, consumers need module loading to work.

## Test Signals
Build tests should cover `DNS_RESOLVER=y`, `m`, and disabled configurations, plus runtime request-key upcalls for CIFS/AFS style descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dns_resolver/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dns_resolver/Makefile -->
# sources/distributed-fs/ceph-client/net/dns_resolver/Makefile

## Purpose
This Makefile wires the DNS resolver implementation into the kernel build.

## Important APIs, Types, And Functions
`obj-$(CONFIG_DNS_RESOLVER) += dns_resolver.o` builds the composite object when enabled. `dns_resolver-y := dns_key.o dns_query.o` links the key type and query upcall implementation into that object.

## Control Flow
Kbuild includes the directory based on `CONFIG_DNS_RESOLVER`, then compiles and links the two implementation files as one built-in object or module.

## State And Persistence
No runtime state is present; this is purely build metadata.

## Dependencies And Integration Points
The file depends on the Kconfig symbol and Kbuild composite-object conventions. The resulting object exports `dns_query()` and registers the `dns_resolver` key type through the implementation files.

## Risks And Edge Cases
Adding new DNS resolver source files requires updating `dns_resolver-y`; otherwise code may compile in isolation but not link into the module.

## Test Signals
Kbuild smoke tests for built-in and module configurations should verify both `dns_key.o` and `dns_query.o` are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dns_resolver/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dns_resolver/dns_key.c -->
# sources/distributed-fs/ceph-client/net/dns_resolver/dns_key.c

## Purpose
This file defines the `dns_resolver` key type used to cache DNS lookup results supplied by userspace request-key upcalls. It validates payload formats, stores successful answers or DNS error codes in key payload slots, implements key matching semantics for DNS descriptions, exposes payloads through key read/describe methods, and initializes credentials used by DNS upcalls.

## Important APIs, Types, And Functions
Key payload words are indexed by `dns_key_data` and `dns_key_error` from `internal.h`. `dns_resolver_preparse()` validates instantiation data and fills `struct key_preparsed_payload`. `dns_resolver_free_preparse()` frees preparsed payloads. `dns_resolver_cmp()` implements case-insensitive matching and ignores a trailing dot in either key description. `dns_resolver_read()` copies cached result bytes to userspace. The file defines and registers `struct key_type key_type_dns_resolver`, and module init/exit functions register/unregister the key type.

It also exports module parameter `dns_resolver_debug` and holds `const struct cred *dns_resolver_cache`, the special credential set used by `dns_query()` to avoid malicious preinstalled redirections.

## Control Flow
For normal hostname results, `dns_resolver_preparse()` requires NUL-terminated data, strips the final NUL from the stored result length, then scans `#`-separated options. The only recognized option is `dnserror=<1..511>`, which stores an error pointer in the error payload slot and intentionally avoids caching a data payload. Unknown or malformed options reject the key with `-EINVAL`.

For non-string server-list payloads, the data must begin with zero and match the version-1 packed server-list header from the DNS resolver UAPI. The content type must be `DNS_PAYLOAD_IS_SERVER_LIST`, the version must be 1, and bad/non-good lookup status gets a very short default expiry when userspace did not provide one. Valid data is copied into a flex-array `struct user_key_payload`.

Key matching compares exact descriptions first, then compares both descriptions case-insensitively after ignoring one trailing dot. Read path validates the key, returns the payload length for size queries, or copies payload data into the caller's buffer.

## State And Persistence
Results are stored in the kernel key retention service. Key payload data persists until key expiry, invalidation, revocation, garbage collection, or module/key type teardown. Error-only keys store an encoded negative errno in `payload.data[dns_key_error]` and no result payload. `dns_resolver_cache` credentials persist while the module is loaded.

## Dependencies And Integration Points
This integrates with `<keys/dns_resolver-type.h>`, `<keys/user-type.h>`, keyctl/request-key infrastructure, DNS resolver UAPI structures, and `dns_query.c`. It depends on userspace instantiating keys through request-key helpers with the expected string or server-list format.

## Risks And Edge Cases
The option parser rejects any option except `dnserror`, so future options require code changes. Error numbers outside 1..511 are rejected. Server-list payload validation checks header content/version but does not fully walk every embedded server/address record here; malformed lengths beyond the basic size can still be a consumer-side risk. Normal result data containing `#` is treated as option-delimited, not literal data. Short expiry for failed server-list lookups intentionally limits negative caching.

## Test Signals
Useful tests instantiate keys with simple results, trailing-dot descriptions, mixed-case lookups, `dnserror` payloads, malformed options, missing NUL termination, valid and invalid server-list headers, and read buffers shorter/longer than the payload. Request-key integration tests should verify `dns_query()` observes error-only and data payloads correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dns_resolver/dns_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dns_resolver/dns_query.c -->
# sources/distributed-fs/ceph-client/net/dns_resolver/dns_query.c

## Purpose
This file implements `dns_query()`, the kernel API that performs DNS resolution by requesting a `dns_resolver` key, causing a userspace upcall when needed, and returning the cached payload to callers.

## Important APIs, Types, And Functions
`dns_query()` is exported. Its inputs are network namespace, optional query type, name and length, request-key options, optional result/expiry outputs, and an `invalidate` flag. It builds key descriptions of the form `[type:]name`, calls `request_key_net()` with `key_type_dns_resolver`, reads `struct user_key_payload`, and optionally invalidates the key after use.

## Control Flow
The function rejects NULL/empty names, empty query types, and names shorter than 3 or longer than 255 bytes. It allocates a description buffer, appends `type:` when present, appends the name, and uses an empty options string if options are NULL. The request is performed under `dns_resolver_cache` credentials through `scoped_with_creds()` to prevent unprivileged users from steering lookups with preinstalled keys.

After `request_key_net()` returns a key, the code takes `rkey->sem` for reading, allows root invalidation/viewing, validates the key, returns a stored DNS error if present, copies payload data with `kmemdup_nul()` when requested, optionally returns key expiry, unlocks, optionally invalidates, and drops the key reference.

## State And Persistence
The function itself keeps no persistent state. Results live in the DNS resolver key cache. Callers own the duplicated `_result` buffer and must free it. When `invalidate` is true, the key is invalidated after the read, forcing a future upcall.

## Dependencies And Integration Points
This depends on `dns_key.c` registering `key_type_dns_resolver`, the keyring/request-key infrastructure, userspace request-key configuration, and network namespaces through `request_key_net()`. It is consumed by kernel filesystem/network clients that need DNS lookups, such as AFS and CIFS.

## Risks And Edge Cases
The name length lower bound of 3 rejects very short names even if a resolver could handle them. If `_result` is NULL, the caller only receives length/expiry/error. The function mutates key flags/permissions while holding the key semaphore, which is expected here but relevant to security review. Userspace helper failures surface as request-key or stored DNS error codes.

## Test Signals
Tests should cover validation failures, successful A/host lookups, typed lookups, namespace-specific upcalls, `_result == NULL`, expiry output, invalidation behavior, DNS error propagation, and memory ownership of the returned buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dns_resolver/dns_query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dns_resolver/internal.h -->
# sources/distributed-fs/ceph-client/net/dns_resolver/internal.h

## Purpose
This private header shares DNS resolver payload slot definitions, credentials, and debug tracing macros between `dns_key.c` and `dns_query.c`.

## Important APIs, Types, And Functions
The enum defines `dns_key_data` and `dns_key_error` payload indexes. It declares `dns_resolver_cache` and `dns_resolver_debug`. `kdebug()`, `kenter()`, and `kleave()` provide conditional debug logging tagged with the current task name.

## Control Flow
The macros emit `KERN_DEBUG` messages only when the module debug parameter is nonzero. `dns_query.c` uses the credential declaration; `dns_key.c` defines it and the payload layout.

## State And Persistence
No state is allocated here. It describes shared global variables owned by the implementation files.

## Dependencies And Integration Points
It includes compiler, kernel, and scheduler headers for `unlikely()`, `printk()`, and `current->comm`. It is internal to `net/dns_resolver`.

## Risks And Edge Cases
The debug mask is treated as boolean by the macros; bitwise debug categories are not implemented despite the parameter being an unsigned integer. Payload indexes must remain consistent with the key type and query code.

## Test Signals
Compile coverage is the main signal. Runtime debug tests can toggle the module parameter and verify traces appear without affecting key behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dns_resolver/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/Kconfig -->
# sources/distributed-fs/ceph-client/net/dsa/Kconfig

## Purpose
This Kconfig file defines the Distributed Switch Architecture core and all DSA tagging-protocol module options built under `net/dsa`.

## Important APIs, Types, And Functions
`menuconfig NET_DSA` is a tristate depending on bridge/HSR compatibility, `INET`, and `NETDEVICES`; it selects `GRO_CELLS`, `NET_SWITCHDEV`, `PHYLINK`, and `NET_DEVLINK`, and implies net selftests. Individual `NET_DSA_TAG_*` symbols select or enable taggers such as no-op, AR9331, Broadcom variants, DSA/EDSA, Mediatek, MaxLinear, Microchip KSZ, Ocelot, QCA, Realtek, Renesas, LAN9303, SJA1105, trailer, VSC73xx, XRS700x, and YT921x.

## Control Flow
Drivers select the tag protocol symbols matching their hardware. Kbuild then compiles corresponding `tag_*.o` modules, while `NET_DSA` controls the core object.

## State And Persistence
The file has no runtime state; it controls built-in/module availability. Runtime tagger selection happens through DSA core and tag driver registration.

## Dependencies And Integration Points
The options integrate DSA with bridge, HSR, switchdev, phylink, devlink, GRO cells, and hardware driver Kconfig files that select appropriate taggers.

## Risks And Edge Cases
If a switch driver omits a required tagger selection, probe may defer or fail with no tagger found. Taggers with extra dependencies, such as `PACKING` for Ocelot and SJA1105, must keep their `select` clauses synchronized with implementation needs.

## Test Signals
Configuration matrix builds should cover `NET_DSA=y/m`, representative taggers as built-in/module, and switch drivers selecting their taggers automatically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/Makefile -->
# sources/distributed-fs/ceph-client/net/dsa/Makefile

## Purpose
This Makefile builds the DSA core composite object, the always-present stubs object when DSA is enabled, and per-protocol tag driver modules.

## Important APIs, Types, And Functions
When `CONFIG_NET_DSA` is set, `stubs.o` is built into `obj-y` so built-in networking code can access the `dsa_stubs` pointer even if DSA is a module. `dsa_core-y` contains `conduit.o`, `devlink.o`, `dsa.o`, `netlink.o`, `port.o`, `switch.o`, `tag.o`, `tag_8021q.o`, `trace.o`, and `user.o`. Each `NET_DSA_TAG_*` symbol maps to a tag driver object. `CFLAGS_trace.o := -I$(src)` helps the trace framework locate `trace.h`.

## Control Flow
Kbuild links the listed core objects into `dsa_core.o` and separately builds tag drivers according to selected symbols. Stubs are built whenever DSA is configured so callers can test and invoke module-provided functionality indirectly.

## State And Persistence
No runtime state exists here.

## Dependencies And Integration Points
This is the build bridge between Kconfig symbols and runtime modules. It also ensures trace compilation has the expected include path.

## Risks And Edge Cases
New core files or tag drivers require Makefile updates. The stubs rule is important for built-in/module split safety; removing it would break built-in network stack calls to optional DSA functionality.

## Test Signals
Build tests should cover built-in DSA, modular DSA, and individual tag driver modules, plus tracing-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/conduit.c -->
# sources/distributed-fs/ceph-client/net/dsa/conduit.c

## Purpose
This file manages DSA conduit devices: the CPU-facing netdevs through which switch traffic enters and leaves the host. It augments conduit ethtool operations with switch-side statistics/registers, exposes a sysfs `dsa/tagging` selector for runtime tag-protocol changes, adjusts MTU/promiscuity for tag overhead, validates hardware timestamp ownership, and handles conduit LAG setup/teardown.

## Important APIs, Types, And Functions
Public functions are `dsa_conduit_setup()`, `dsa_conduit_teardown()`, `dsa_conduit_lag_setup()`, `dsa_conduit_lag_teardown()`, and `__dsa_conduit_hwtstamp_validate()`. Internal ethtool wrappers are `dsa_conduit_get_regs_len()`, `dsa_conduit_get_regs()`, `dsa_conduit_get_ethtool_stats()`, `dsa_conduit_get_ethtool_phy_stats()`, `dsa_conduit_get_sset_count()`, and `dsa_conduit_get_strings()`.

The sysfs attribute `tagging` uses `dsa_tag_protocol_to_str()`, `dsa_tag_driver_get_by_name()`, `dsa_tree_change_tag_proto()`, and `dsa_tag_driver_put()` to switch the active tagger.

## Control Flow
Setup computes conduit MTU as Ethernet payload plus tag overhead, creates a device link from switch to conduit parent when possible, sets MTU, publishes `dev->dsa_ptr` after a write barrier, forces promiscuity if required by the tagger or missing unicast filtering, installs ethtool wrappers, and creates the sysfs group. Teardown removes sysfs, restores original ethtool ops, resets MTU to `ETH_DATA_LEN`, drops promiscuity, clears `dsa_ptr`, and issues another write barrier.

Ettool wrappers first call original conduit operations when present, then append CPU/DSA port data from every shared DSA port in the tree with stable string prefixes `sXX_pXX_`. HWTSTAMP validation rejects timestamping on the conduit if any switch port supports hardware timestamping, steering timestamp configuration to DSA user ports.

LAG setup ensures the LAG master is a conduit if not already, then joins the CPU port to the LAG. Teardown leaves the LAG and only tears down the conduit when no DSA user upper remains.

## State And Persistence
Runtime state is stored in `dev->dsa_ptr`, `cpu_dp->orig_ethtool_ops`, conduit MTU/promiscuity, sysfs group membership, and LAG membership in `struct dsa_port`. All state is in kernel memory and unwound during tree teardown or LAG leave.

## Dependencies And Integration Points
The file integrates with netdev ethtool ops, sysfs, device links, LAG netdevs, DSA tag drivers, `dsa_tree_change_tag_proto()`, port LAG helpers, phylink/hwtstamp policy, and DSA receive routing via `dev->dsa_ptr`.

## Risks And Edge Cases
Failure after MTU adjustment but before full setup currently unwinds promiscuity and ethtool state but does not reset MTU in the early error path. Runtime tagger switching depends on driver support and must restore module references correctly on failure. LAG teardown scans uppers under RCU assumptions; callers must satisfy locking expectations. `dsa_conduit_get_strings()` assumes original `ops` is non-NULL in one branch, so conduit devices without ethtool ops need careful coverage.

## Test Signals
Tests should cover conduit setup/teardown, ethtool stats/register aggregation, tagger sysfs show/store success/failure, MTU changes for tag overhead, hwtstamp rejection when a switch supports timestamping, and CPU-port LAG join/leave rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/conduit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/conduit.h -->
# sources/distributed-fs/ceph-client/net/dsa/conduit.h

## Purpose
This private header declares the conduit management API used by DSA setup, user-port migration, and stubs.

## Important APIs, Types, And Functions
It forward-declares `struct dsa_port`, `struct net_device`, `struct netdev_lag_upper_info`, and `struct netlink_ext_ack`, then declares setup/teardown for normal conduit devices and LAG conduits plus `__dsa_conduit_hwtstamp_validate()`.

## Control Flow
No executable control flow exists here. The declarations are implemented in `conduit.c` and called from `dsa.c`, `user.c`, and the DSA stubs registration path.

## State And Persistence
No state is stored in the header.

## Dependencies And Integration Points
The header is the local interface between conduit handling and the rest of DSA core. The hwtstamp declaration is also exposed through `dsa_stubs` for core netdev code.

## Risks And Edge Cases
Because the header does not include all type definitions, users must include appropriate networking headers before using the declared types in code that needs their fields.

## Test Signals
Compile coverage confirms signature consistency. Runtime coverage comes from conduit setup and hwtstamp validation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/conduit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/devlink.c -->
# sources/distributed-fs/ceph-client/net/dsa/devlink.c

## Purpose
This file adapts DSA switch and port objects to the generic devlink subsystem. It provides devlink ops callbacks that forward to optional `dsa_switch_ops`, helper exports for DSA drivers to register params/resources/regions, and per-port devlink port lifecycle during DSA port setup.

## Important APIs, Types, And Functions
`dsa_devlink_ops` implements devlink info and shared-buffer callbacks by translating from `struct devlink` or `struct devlink_port` back to `struct dsa_switch` and port index. Exported helpers include `dsa_devlink_param_get()`, `dsa_devlink_param_set()`, `dsa_devlink_params_register()`, `dsa_devlink_params_unregister()`, resource register/unregister and occupancy helpers, region create/destroy helpers, `dsa_port_devlink_setup()`, `dsa_port_devlink_teardown()`, `dsa_switch_devlink_alloc()`, `dsa_switch_devlink_free()`, `dsa_switch_devlink_register()`, and `dsa_switch_devlink_unregister()`.

## Control Flow
Switch setup allocates a devlink with `devlink_alloc()`, stores the owning `struct dsa_switch` in private data, lets switch setup add devlink objects, then registers devlink after the switch is ready. Port setup initializes a `devlink_port`, optionally calls driver `port_setup`, sets attributes with tree index as switch ID and flavour based on DSA port type, then registers the port. Teardown unregisters the devlink port, calls optional driver `port_teardown`, and finalizes the port object.

Driver-facing resource helpers lock `ds->devlink` for devl resource operations. Param helpers are thin callback shims and registration wrappers. Region helpers attach either to the switch devlink or a specific DSA devlink port.

## State And Persistence
The main state is `ds->devlink` and each `dp->devlink_port`. Devlink params, resources, regions, and shared-buffer objects persist while registered by drivers and are removed during switch/port teardown.

## Dependencies And Integration Points
This integrates DSA with `net/devlink.h`, driver callbacks in `struct dsa_switch_ops`, devlink resources, devlink params, devlink regions, and devlink ports. It is called from `dsa.c` port and switch setup paths.

## Risks And Edge Cases
Most devlink ops return `-EOPNOTSUPP` when a switch driver lacks a callback; userspace must handle optional capability. Port setup must call driver `port_teardown` on devlink port registration failure, and this file does. The switch ID is derived from the tree index only, so multi-tree uniqueness relies on that index.

## Test Signals
Tests should verify devlink registration for switches and all port flavours, callback forwarding, optional callback absence, param/resource/region registration from drivers, and failure rollback in port registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/devlink.h -->
# sources/distributed-fs/ceph-client/net/dsa/devlink.h

## Purpose
This private header declares the DSA core devlink lifecycle API used by switch and port setup.

## Important APIs, Types, And Functions
It declares `dsa_port_devlink_setup()`, `dsa_port_devlink_teardown()`, `dsa_switch_devlink_register()`, `dsa_switch_devlink_unregister()`, `dsa_switch_devlink_alloc()`, and `dsa_switch_devlink_free()`.

## Control Flow
No executable logic is present. `dsa.c` calls these functions as part of switch-tree setup and teardown.

## State And Persistence
No state is stored here; it describes functions that manage `ds->devlink` and `dp->devlink_port`.

## Dependencies And Integration Points
It forward-declares `struct dsa_port` and `struct dsa_switch` to keep include dependencies light.

## Risks And Edge Cases
Signature changes must stay synchronized with `devlink.c` and `dsa.c`; otherwise DSA core build breaks.

## Test Signals
Compile coverage and DSA probe/teardown tests exercise the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/dsa.c -->
# sources/distributed-fs/ceph-client/net/dsa/dsa.c

## Purpose
This is the central DSA topology and switch lifecycle manager. It owns switch-tree discovery, CPU/DSA/user port parsing, routing table construction, tag-protocol binding and runtime switching, switch and port setup/teardown ordering, conduit setup, LAG/bridge numbering state, module init/exit, and exported entry points used by hardware switch drivers.

## Important APIs, Types, And Functions
Global state includes `dsa_tree_list`, `dsa2_mutex`, ordered workqueue `dsa_owq`, and the forwarding-offload bridge bitmap. Exported APIs include `dsa_register_switch()`, `dsa_unregister_switch()`, `dsa_switch_shutdown()`, `dsa_switch_suspend()`, `dsa_switch_resume()`, `dsa_switch_find()`, `dsa_port_from_netdev()`, `dsa_flush_workqueue()`, `dsa_db_equal()`, `dsa_fdb_present_in_other_db()`, `dsa_mdb_present_in_other_db()`, simple HSR helpers, LAG mapping helpers, bridge numbering helpers, conduit state change helpers, and `dsa_tree_change_tag_proto()`.

Key internal flows are `dsa_tree_touch()/put()`, `dsa_switch_parse_of()`, `dsa_switch_parse()`, `dsa_tree_setup()`, `dsa_switch_setup()`, `dsa_port_setup()`, `dsa_tree_setup_conduit()`, `dsa_tree_teardown()`, and `dsa_switch_release_ports()`.

## Control Flow
Driver probe calls `dsa_register_switch()`, which serializes under `dsa2_mutex`, parses OF or platform data, touches/allocates a switch tree, allocates all `struct dsa_port` objects, resolves CPU conduit netdevs, picks a tag protocol, and attempts `dsa_tree_setup()`. Tree setup first builds routing links from DSA port phandles; if the tree is incomplete it returns success without setting up until more switches probe. For a complete tree it assigns CPU ports, sets up each switch, sets up shared CPU/DSA ports before user ports, sets up conduits, allocates LAG ID space, and marks the tree setup.

Switch setup allocates devlink, registers the switch notifier, calls driver `setup`, synchronizes the selected tag protocol with the driver, optionally registers a user MDIO bus, registers devlink, and sets `ds->setup`. Port setup creates devlink ports, registers phylink for CPU/DSA ports when firmware describes links, enables shared ports, and creates user netdevs for user ports. User-port setup failure downgrades the port to unused if possible.

Runtime tag-protocol changes run under RTNL: disconnect old taggers, notify switches, bind the new tagger, change driver tag protocol, update CPU port receive callbacks and user MTUs, and roll back to the old tagger on failure. Removal and shutdown reverse setup, detach conduit/user relationships, clean leaked FDB/MDB/VLAN bookkeeping, and drop tree references.

## State And Persistence
DSA state is in heap-allocated `struct dsa_switch_tree`, `struct dsa_switch`, `struct dsa_port`, `struct dsa_link`, LAG arrays, bridge objects, and per-port address/VLAN lists. It persists while switch drivers are registered. Tree references are kref-managed. CPU conduit netdevs are held with netdev trackers and released during port cleanup.

## Dependencies And Integration Points
This file integrates with device tree, platform data, netdev and RTNL locking, phylink, MDIO, devlink, DSA tag drivers, switchdev user-port code, conduit handling, DSA notifiers, HSR, LAG, bridge offload numbering, and stubs for built-in network stack callers.

## Risks And Edge Cases
Incomplete multi-switch trees return success without setup, so later probes must complete the routing table. A DSA tree may use only one tag protocol; mismatches across CPU ports or switches fail setup. Device-tree CPU ports without resolvable conduit netdevs defer probe. Removal cleans leaked FDB/MDB/VLAN entries but those logs indicate upper-layer tracking bugs. Runtime tagger switching has multiple rollback paths and depends on both tagger and switch callbacks behaving consistently. Bridge-number allocation is limited by `BITS_PER_LONG`.

## Test Signals
Strong tests include OF parsing for complete/incomplete trees, platform-data parsing, multi-CPU-port default assignment, tagger autoload and override, setup/teardown rollback at every stage, conduit state replay, switch unregister cleanup, suspend/resume, shutdown unlinking, FDB/MDB duplicate database detection, and HSR simple offload helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/dsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/dsa.h -->
# sources/distributed-fs/ceph-client/net/dsa/dsa.h

## Purpose
This private header exposes DSA core helpers shared across `dsa.c`, conduit, port, switch, tag, and user handling.

## Important APIs, Types, And Functions
It declares the global `dsa_tree_list`, database comparison, ordered work scheduling, LAG map/unmap/find helpers, first conduit lookup, runtime tag-protocol change, conduit admin/oper state notification helpers, bridge number get/put/find helpers, and bridge lookup.

## Control Flow
The header has no executable logic. Its functions are implemented mainly in `dsa.c` and called by the rest of DSA core.

## State And Persistence
The only declared state is `dsa_tree_list`, the global list of switch trees. Other declarations manipulate tree, bridge, and LAG runtime state owned elsewhere.

## Dependencies And Integration Points
It forward-declares DSA and netdev types to keep local includes lightweight. It is the glue for DSA internal modules that need topology state but not full public API exposure.

## Risks And Edge Cases
Because many declarations manipulate global topology, callers must obey locking expectations from implementations, especially `dsa2_mutex` and RTNL contexts.

## Test Signals
Compile coverage plus DSA probe, LAG, bridge, conduit state, and tagger-change tests exercise these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/dsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/netlink.c -->
# sources/distributed-fs/ceph-client/net/dsa/netlink.c

## Purpose
This file defines the rtnetlink link operations for DSA user interfaces. It exposes and changes the conduit netdev associated with a DSA user port through `IFLA_DSA_CONDUIT`.

## Important APIs, Types, And Functions
`dsa_policy` validates `IFLA_DSA_CONDUIT` as a `u32` ifindex. `dsa_changelink()` handles requested conduit changes by resolving the ifindex and calling `dsa_user_change_conduit()`. `dsa_get_size()` and `dsa_fill_info()` report the current conduit ifindex. `struct rtnl_link_ops dsa_link_ops` registers kind `"dsa"` with these callbacks and `netns_refund = true`.

## Control Flow
`dsa.c` registers `dsa_link_ops` at module init. Netlink change requests pass through validation, lookup the target conduit in the same net namespace, and delegate the complex migration to user/port code. Dump/getlink paths serialize the current conduit.

## State And Persistence
This file stores no per-interface state. It reads and mutates DSA user state through `dsa_user_to_conduit()` and `dsa_user_change_conduit()`.

## Dependencies And Integration Points
It integrates with rtnetlink, UAPI `IFLA_DSA_*` attributes, DSA user netdevs, and conduit migration code in `user.c`/`port.c`.

## Risks And Edge Cases
An invalid ifindex returns `-EINVAL`; deeper validation of whether the netdev can be a conduit is delegated. Changing conduits live is high-risk because host FDB/MDB/VLAN and bridge offload state must migrate.

## Test Signals
Netlink tests should read `IFLA_DSA_CONDUIT`, attempt valid and invalid conduit changes, verify extack failures, and check that traffic and bridge/VLAN state survive a successful migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/netlink.h -->
# sources/distributed-fs/ceph-client/net/dsa/netlink.h

## Purpose
This private header exposes the DSA rtnetlink link-ops object to module initialization.

## Important APIs, Types, And Functions
It declares `extern struct rtnl_link_ops dsa_link_ops __read_mostly`.

## Control Flow
No executable logic exists. `dsa.c` registers and unregisters `dsa_link_ops`; `netlink.c` defines it.

## State And Persistence
The declared object is read-mostly global rtnetlink operation metadata.

## Dependencies And Integration Points
It connects DSA module init/exit with the rtnetlink implementation without exposing internals elsewhere.

## Risks And Edge Cases
Signature or storage changes must stay synchronized with `netlink.c`.

## Test Signals
Compile and module init tests cover the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/port.c -->
# sources/distributed-fs/ceph-client/net/dsa/port.c

## Purpose
This file implements operations on one DSA port: enabling/disabling, bridge and LAG join/leave, STP/MST state, VLAN filtering, FDB/MDB/VLAN/MRP operations, host address and VLAN programming, MTU propagation, phylink setup for shared ports, CPU-conduit migration, HSR offload hooks, and tag_8021q VLAN notifications.

## Important APIs, Types, And Functions
Public functions include `dsa_port_supports_hwtstamp()`, `dsa_port_set_state()`, `dsa_port_set_mst_state()`, enable/disable variants, `dsa_port_bridge_join()/leave()`, LAG helpers, `dsa_port_vlan_filtering()`, `dsa_port_skip_vlan_configuration()`, `dsa_port_ageing_time()`, bridge flag and MST helpers, FDB/MDB/VLAN host and user operations, MRP helpers, `dsa_port_change_conduit()`, `dsa_port_set_tag_protocol()`, `dsa_supports_eee()`, phylink create/destroy, shared-port link register/unregister, HSR join/leave, and tag_8021q VLAN add/del.

## Control Flow
Bridge join creates or references a `struct dsa_bridge`, broadcasts `DSA_NOTIFIER_BRIDGE_JOIN`, registers switchdev offload for the bridge port, and synchronizes bridge flags, STP state, VLAN filtering, and ageing time. Rollback unoffloads, flushes deferred work, broadcasts leave, and destroys the bridge object. Bridge leave unoffloads earlier through `pre_bridge_leave()`, destroys the bridge reference, broadcasts leave, resets standalone flags/STP/VLAN filtering, and preserves ageing time.

LAG join creates or references `struct dsa_lag`, notifies the tree, and if the LAG is already under a bridge, also joins that bridge. Leave unwinds bridge membership first, destroys the LAG reference, and notifies. VLAN filtering validates VLAN upper conflicts and global filtering constraints under RCU, calls driver `port_vlan_filtering`, updates standalone VLAN management, and synchronizes host flooding. FDB/MDB/VLAN operations package notifier payloads with the appropriate database identity: port, bridge, or LAG.

`dsa_port_change_conduit()` is the most complex path. It temporarily unoffloads bridge state, disables standalone VLAN filtering if needed, unsyncs host addresses, uninstalls live host UC, calls driver `port_change_conduit`, inherits MAC address if necessary, reinstalls addresses, restores VLANs, and rejoins the bridge. Multiple rewind labels attempt to restore the old conduit and old offload state on failure.

Phylink setup validates required OF link properties for CPU/DSA ports, allows legacy workarounds for known switches, creates phylink, and connects PHY/fixed links when described.

## State And Persistence
Port state lives in `struct dsa_port`: bridge and LAG references, STP state, learning, ageing time, VLAN filtering, CPU port affinity, hsr device, phylink pointer/config, tag receive callback, address/VLAN lists, and user netdev association. Bridge and LAG objects are refcounted across ports.

## Dependencies And Integration Points
This file bridges DSA with switchdev, bridge, VLAN, MST, LAG, HSR, MRP, phylink, OF, netlink extack, DSA notifiers in `switch.c`, tag_8021q, and user netdev helpers.

## Risks And Edge Cases
Global VLAN filtering constraints can reject bridge configurations spanning multiple bridges. VLAN uppers with overlapping bridge VIDs block enabling VLAN awareness. Conduit migration has many partial-failure paths and logs restoration failures but may still leave external state degraded if restoration fails. Shared-port OF validation has a legacy compatible whitelist; new hardware should not rely on missing link descriptions. Some driver callbacks are optional and return `-EOPNOTSUPP`, which higher layers intentionally ignore in selected cases.

## Test Signals
Tests should cover bridge join/leave rollback, LAG under bridge transitions, VLAN filtering with VLAN uppers and global filtering, FDB/MDB/VLAN notifier payloads, host address install/remove, conduit migration success and forced failures, phylink validation, HSR join/leave, MST fast ageing, MRP ops, and tag_8021q notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/port.h -->
# sources/distributed-fs/ceph-client/net/dsa/port.h

## Purpose
This private header declares the DSA per-port operation surface shared across core, user netdev, switch notifier, conduit, and tag code.

## Important APIs, Types, And Functions
It declares bridge, LAG, VLAN filtering, ageing, MST, bridge flags, MTU, FDB/MDB, host FDB/MDB, VLAN, MRP, phylink, shared-port link, HSR, tag_8021q, host flood, and conduit-change helpers. It also declares `dsa_port_supports_hwtstamp()` and `dsa_port_set_tag_protocol()`.

## Control Flow
No executable flow is present. The declarations mirror implementation in `port.c` and are invoked by `dsa.c`, `switch.c`, `conduit.c`, `tag.h`, and user-port code.

## State And Persistence
The header has no state. Declared functions manipulate `struct dsa_port` state owned by the DSA tree.

## Dependencies And Integration Points
It includes `<net/dsa.h>` and forward-declares bridge, lag, switchdev, phy, and netlink types so DSA internal files can share port functionality.

## Risks And Edge Cases
This is a broad internal API; changes to semantics such as whether `-EOPNOTSUPP` is ignorable must be audited across many callers.

## Test Signals
Compile coverage plus bridge, LAG, VLAN, FDB/MDB, MRP, phylink, and conduit migration tests exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/stubs.c -->
# sources/distributed-fs/ceph-client/net/dsa/stubs.c

## Purpose
This file defines the global DSA stubs pointer used by built-in networking code to call optional DSA functionality when DSA may be modular.

## Important APIs, Types, And Functions
It defines and exports `const struct dsa_stubs *dsa_stubs`.

## Control Flow
There is no control flow in this file. `dsa.c` assigns `dsa_stubs` to its static implementation table during module init and clears it during exit.

## State And Persistence
`dsa_stubs` is global pointer state. It is NULL when DSA is not active and points to DSA implementations while the DSA core module is loaded.

## Dependencies And Integration Points
It includes `<net/dsa_stubs.h>` and is built into `obj-y` when DSA is configured, allowing built-in callers to check the pointer without directly linking against a possibly modular DSA core.

## Risks And Edge Cases
Callers must handle NULL and avoid retaining stale function pointers across module unload. Synchronization expectations are defined by the users of the stub table.

## Test Signals
Build tests for modular DSA and runtime tests for hwtstamp validation through the stubs pointer are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/stubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/switch.c -->
# sources/distributed-fs/ceph-client/net/dsa/switch.c

## Purpose
This file handles switch-wide reactions to DSA notifier events. It translates bridge, LAG, FDB, MDB, VLAN, MTU, ageing-time, tag-protocol, tag_8021q, and conduit-state notifications into driver callbacks, while maintaining refcounted shared-port and LAG programming state.

## Important APIs, Types, And Functions
Public functions are `dsa_vlan_find()`, `dsa_tree_notify()`, `dsa_broadcast()`, `dsa_switch_register_notifier()`, and `dsa_switch_unregister_notifier()`. The central dispatcher is `dsa_switch_event()`. Internal helpers include `dsa_switch_ageing_time()`, `dsa_switch_mtu()`, bridge join/leave, FDB/MDB add/delete for user, host, and LAG databases, VLAN add/delete for user and host paths, tag protocol connect/disconnect/change, and conduit-state forwarding.

Notifier payload types are declared in `switch.h` and carry the source port, database identity, bridge/LAG state, VLAN object, extack, MTU, or tag ops.

## Control Flow
Ports call `dsa_port_notify()` or `dsa_broadcast()`, which invokes raw notifier chains registered per switch tree. Each switch receives `dsa_switch_event()` and handles only events relevant to it. Cross-chip bridge/LAG callbacks are invoked when the event source is on another switch and the driver supports cross-chip operations.

FDB/MDB/VLAN programming is direct for user ports but refcounted for CPU and DSA shared ports because multiple user ports or databases can require the same hardware entry. Add paths search the local list, bump refcount if present, or program hardware and allocate bookkeeping. Delete paths decrement refcount and only remove hardware on the last reference; hardware delete failure restores the refcount. LAG FDBs are similarly refcounted on `struct dsa_lag`.

Ageing time programming selects the fastest active port ageing time for chips with a shared setting. MTU changes apply to the targeted user port plus CPU/DSA ports. Tag-protocol change first calls driver `change_tag_protocol`, updates CPU port receive callbacks, then refreshes user tagger setup and MTU. Connect/disconnect events notify both tagger callbacks and optional switch callbacks.

## State And Persistence
State is stored in per-port `fdbs`, `mdbs`, and `vlans` lists protected by mutexes, LAG FDB lists protected by `lag->fdb_lock`, and switch notifier registrations in each tree's raw notifier head. This state persists for the life of the DSA tree and is cleaned during port/switch release.

## Dependencies And Integration Points
This file integrates DSA port code, switch driver callbacks, switchdev bridge objects, VLAN objects, LAGs, tag_8021q, runtime tagger switching, tracing, and raw notifier chains.

## Risks And Edge Cases
Reference counting shared hardware entries is correctness-critical; missed deletes leave stale FDB/MDB/VLAN entries, while extra deletes remove entries still needed by another database. Some callbacks return `-EOPNOTSUPP`; callers may treat it as acceptable depending on event type. `dsa_broadcast()` warns it is unreliable during asynchronous probe because not all trees may exist. Tagger connect failures must unwind tagger-side state to avoid leaks.

## Test Signals
Tests should exercise notifier dispatch for each event, shared-port FDB/MDB/VLAN refcount add/delete, hardware delete failures, cross-chip bridge/LAG callbacks, ageing-time bounds, MTU propagation, tag protocol change/connect/disconnect, tag_8021q VLAN propagation, and conduit-state notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/switch.h -->
# sources/distributed-fs/ceph-client/net/dsa/switch.h

## Purpose
This private header defines DSA notifier event IDs, event payload structures, and switch notifier APIs shared by port, switch, and tree code.

## Important APIs, Types, And Functions
The enum lists all `DSA_NOTIFIER_*` events: ageing time, bridge join/leave, FDB/MDB host and user operations, LAG changes and FDB operations, VLAN host and user operations, MTU, tag-protocol change/connect/disconnect, tag_8021q VLAN add/delete, and conduit-state changes. Payload structs include `dsa_notifier_bridge_info`, `dsa_notifier_fdb_info`, `dsa_notifier_lag_info`, `dsa_notifier_vlan_info`, `dsa_notifier_mtu_info`, `dsa_notifier_tag_proto_info`, and others.

It declares `dsa_vlan_find()`, `dsa_tree_notify()`, `dsa_broadcast()`, `dsa_switch_register_notifier()`, and `dsa_switch_unregister_notifier()`.

## Control Flow
No executable logic is present. The event definitions determine dispatch in `switch.c` and call sites in `port.c`, `dsa.c`, and tag_8021q code.

## State And Persistence
No state is stored here. Payload structs carry transient event data across notifier calls.

## Dependencies And Integration Points
It includes `<net/dsa.h>` for DSA data structures and forward-declares extack. It is the contract for cross-chip and cross-module DSA event propagation.

## Risks And Edge Cases
Adding a notifier ID requires updating `dsa_switch_event()` and all expected producers/consumers. Payload lifetime must outlive synchronous raw notifier delivery.

## Test Signals
Compile coverage plus notifier tests for every event type validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/switch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag.c

## Purpose
This file implements generic DSA tag driver registration/lookup and the packet receive demultiplexer for tagged frames arriving on DSA conduit devices.

## Important APIs, Types, And Functions
Global state is `dsa_tag_drivers_list` protected by `dsa_tag_drivers_lock`. The packet handler is `dsa_switch_rcv()`, registered through `struct packet_type dsa_pack_type` for `ETH_P_XDSA`. Exported tagger APIs are `dsa_tag_drivers_register()`, `dsa_tag_drivers_unregister()`, `dsa_tag_driver_get_by_name()`, `dsa_tag_driver_get_by_id()`, `dsa_tag_driver_put()`, and `dsa_tag_protocol_to_str()`.

## Control Flow
Module init in `dsa.c` calls `dev_add_pack(&dsa_pack_type)`. On RX, `dsa_switch_rcv()` verifies `dev->dsa_ptr`, unshares the skb, optionally handles hardware port-mux metadata by mapping port ID to a DSA user device, otherwise calls the CPU port tagger receive callback. It then restores Ethernet header context, runs `eth_type_trans()`, handles packets injected directly to upper devices, optionally software-untags VLANs for bridge PVID behavior, updates software stats, defers PTP timestamp delivery when the switch driver asks, and finally submits to GRO cells.

Tag drivers register static `struct dsa_tag_driver` objects. Lookup by name or ID first requests the module alias, then searches the list and pins the owner module with `try_module_get()`. Callers must release with `dsa_tag_driver_put()`.

## State And Persistence
Registered taggers remain in the global list while their modules are loaded. Lookup takes module references. RX uses per-conduit `dev->dsa_ptr` and per-CPU-port receive callbacks set during DSA setup or tagger change.

## Dependencies And Integration Points
This integrates with Linux packet handlers, skb metadata destinations, DSA tagger modules, DSA user netdev private data, GRO cells, PTP classification/timestamp callbacks, bridge VLAN software untagging from `tag.h`, and conduit setup.

## Risks And Edge Cases
Packets arriving after conduit teardown see NULL `dsa_ptr` and are dropped. Tagger receive callbacks must return a valid user skb or NULL to drop. Hardware metadata path assumes device 0 in `dsa_conduit_find_user()`. PTP timestamp deferral depends on temporary header push/pull and switch driver ownership of the skb. Module reference handling is mandatory around runtime tagger changes.

## Test Signals
Tests should cover tagger registration/unregistration, module autoload aliases, lookup by name and ID, RX demux through tag callback and metadata path, VLAN untagging behavior, PTP timestamp deferral, GRO delivery, and drop behavior for NULL `dsa_ptr` or unknown ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag.h -->
# sources/distributed-fs/ceph-client/net/dsa/tag.h

## Purpose
This private header defines DSA tag driver metadata, tagger registration macros, RX/TX helper functions for taggers, VLAN software untagging helpers, and module alias conventions.

## Important APIs, Types, And Functions
`struct dsa_tag_driver` binds `struct dsa_device_ops` to a list node and owner module. The header declares tagger lookup/refcount APIs and `dsa_pack_type`. Inline helpers include `dsa_tag_protocol_overhead()`, `dsa_conduit_find_user()`, `dsa_software_vlan_untag()`, bridge PVID untag helpers, `dsa_find_designated_bridge_port_by_vid()`, `dsa_default_offload_fwd_mark()`, EtherType header strip/allocate/position helpers, and `dsa_xmit_port_mask()`.

Macros define module aliases (`dsa_tag:<name>` and `dsa_tag:id-<proto>`), `DSA_TAG_DRIVER()`, `module_dsa_tag_driver()`, and `module_dsa_tag_drivers()`.

## Control Flow
Tagger modules use the macros to create static driver objects and module init/exit functions that register/unregister them with `tag.c`. TX helpers manipulate skb headroom for taggers that insert EtherType-like headers. RX helpers locate user netdevs, clear hardware-accelerated VLAN tags when bridge semantics require software untagging, and compute HSR duplicate port masks.

`dsa_software_vlan_untag()` first finds the ingress DSA user port's bridge, moves inline VLAN tags to hwaccel if needed, obtains the VID, and clears the tag depending on VLAN-aware or VLAN-unaware bridge settings. The VLAN-unaware helper contains an explicit FIXME: it currently assumes the private VID equals the bridge PVID.

## State And Persistence
The header stores no global state, but its helpers read DSA tree port lists, bridge membership, tagger operation fields, skb VLAN metadata, and HSR port state.

## Dependencies And Integration Points
It depends on VLAN, bridge VLAN APIs, public `<net/dsa.h>`, DSA port/user helpers, skb layout conventions, HSR feature flags, and tag driver modules.

## Risks And Edge Cases
The VLAN-unaware untagging FIXME is a known correctness risk for drivers whose private VID differs from bridge PVID. Header manipulation helpers require callers to have already pushed/pulled the expected bytes. `dsa_conduit_find_user()` matches by switch index and port; stacked or metadata-driven paths must provide the right device/port tuple. Macro-generated module init/exit allows only one use per module.

## Test Signals
Tests should cover tagger module alias generation, skb header helpers with headroom/tailroom, VLAN-aware and VLAN-unaware software untagging, designated bridge port selection by VID, HSR port mask generation, and lookup of user devices in multi-switch trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag.h -->
