# subset-b-006239 Research

Work item: `subset-b-006239`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/Kconfig -->
# sources/distributed-fs/ceph-client/net/netfilter/Kconfig

## Purpose

This Kconfig file is the main configuration surface for the kernel netfilter stack under `net/netfilter`. It gates ingress and egress hooks, nfnetlink interfaces, connection tracking, NAT, nf_tables, flow tables, xtables targets, xtables matches, and then includes the ipset and IPVS submenus. It is a build-time policy document rather than runtime code, but it directly controls which modules from the neighboring Makefile can be built and which symbols other networking code may rely on.

## Important Symbols And Dependencies

The top-level menu depends on `INET && NETFILTER`. Early symbols enable core hook families and integration points: `NETFILTER_INGRESS` selects `NET_INGRESS`, `NETFILTER_EGRESS` selects `NET_EGRESS`, `NETFILTER_SKIP_EGRESS` is enabled when egress hooks coexist with `NET_CLS_ACT` or `IFB`, and `NETFILTER_BPF_LINK` follows `BPF_SYSCALL`. The nfnetlink options select `NETFILTER_NETLINK` for accounting, queueing, logging, OS fingerprinting, and base hook dump support.

`NF_CONNTRACK` selects IPv4 defragmentation and IPv6 defragmentation when IPv6 is present. Its nested options control marks, secmarks, zones, procfs export, events, timeout extension, timestamps, labels, protocol helpers, and application helpers. `NF_NAT` depends on conntrack and has helper-specific defaults that mirror the corresponding conntrack helper.

`NF_TABLES` selects `NETFILTER_NETLINK` and `NET_CRC32C`, then exposes nftables families and expressions such as CT, flow offload, NAT, queue, quota, reject, compat, fib, socket, OSF, tproxy, xfrm, synproxy, and flow table support. `NETFILTER_XTABLES` exposes legacy x_tables plus many targets and matches, with dependencies that pull in conntrack, NAT, textsearch, socket lookup, bridge, XFRM, LED, IPVS, and protocol-specific features.

## Control Flow And State

Kconfig evaluation determines the symbol graph. Many options are only visible with `NETFILTER_ADVANCED`; when advanced mode is off, several common modules default to `m`, preserving common firewall functionality without exposing the full menu. Nested `if NF_CONNTRACK`, `if NF_TABLES`, and `if NETFILTER_XTABLES` blocks shape the feature families and ensure impossible combinations are not presented. The final `source` lines include `net/netfilter/ipset/Kconfig` and `net/netfilter/ipvs/Kconfig`, so ipset and IPVS are subordinate configuration trees.

The file has no runtime persistence, but selected symbols persist in `.config` and become ABI-affecting build inputs. Defaults such as `CONFIG_NF_CONNTRACK=m`, `CONFIG_NETFILTER_NETLINK_LOG=m`, and many xtables defaults in non-advanced mode influence which modules are available on a deployed system.

## Integration Points

The file integrates with `net/netfilter/Makefile`, which maps these symbols to objects. It also integrates with IPv4/IPv6 Kconfig trees through dependencies such as `IP_NF_RAW`, `IP6_NF_RAW`, `NF_TABLES_IPV4`, and `NF_TABLES_IPV6`; with tc/netdev through ingress and egress; with BPF through `NETFILTER_BPF_LINK`; with XFRM, IPVS, bridge netfilter, textsearch, LED triggers, and lwtunnel through conditional symbols.

## Risks

The main risk is dependency drift: adding an object in the Makefile without a matching Kconfig symbol, or adding a symbol here without the needed `select`/`depends on`, can create link failures or unusable modules. Defaults under `NETFILTER_ADVANCED=n` are security-sensitive because they quietly build packet filtering, logging, conntrack, and NAT helpers. Another risk is hidden feature coupling: many xtables targets select helper modules, defragmentation, or NAT subfeatures, so changing one dependency can break runtime rules that appear unrelated.

## Test Signals

Useful signals are `make olddefconfig`, `make allmodconfig`, and targeted builds for `net/netfilter/`. Runtime smoke tests should exercise nf_tables, xtables, nfqueue/nflog, conntrack, NAT, ingress/egress hook registration, and ipset/IPVS menus under common IPv4-only, IPv6, and module/built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/Makefile -->
# sources/distributed-fs/ceph-client/net/netfilter/Makefile

## Purpose

This Makefile maps netfilter Kconfig symbols to kernel objects and composite modules. It is the build assembly point for core netfilter, nfnetlink modules, conntrack, NAT, nf_tables, flow tables, xtables matches and targets, ipset, IPVS, and lwtunnel hooks.

## Important Build Rules

`netfilter-objs := core.o nf_log.o nf_queue.o nf_sockopt.o utils.o` defines the built core module assembled when `CONFIG_NETFILTER` is enabled. `nf_conntrack-y` and `nf_nat-y` define composite objects for connection tracking and NAT, with optional members added by Kconfig symbols such as timeout, timestamp, events, labels, OVS, SCTP, GRE, redirect, masquerade, and BTF support. BTF object inclusion differs for module versus built-in builds using `CONFIG_DEBUG_INFO_BTF_MODULES` and `CONFIG_DEBUG_INFO_BTF`.

The file registers one object per nfnetlink subsystem, helper, nftables expression, flow table component, x_tables target, and x_tables match. `nf_tables-objs` includes the nftables core and built-in expression/set implementations, conditionally adding `nft_set_pipapo_avx2.o` on x86_64 non-UML and `nft_ct_fast.o` when `CONFIG_NFT_CT` and retpoline mitigation are configured. The ipset and IPVS directories are included with `obj-$(CONFIG_IP_SET) += ipset/` and `obj-$(CONFIG_IP_VS) += ipvs/`.

## Control Flow And State

The control flow is Kbuild symbol expansion. `obj-$(CONFIG_...)` emits objects for built-in `y` or module `m`, while composite `foo-y` variables define module internals. Conditional `ifeq`, `ifdef`, and `ifndef` blocks adjust object composition for debug BTF, architecture acceleration, retpoline support, and UML exclusions.

There is no runtime state. The persistent effect is the generated build graph, module names, and built-in object composition derived from `.config`.

## Dependencies And Integration

This file must stay aligned with `net/netfilter/Kconfig` and the actual source files in the same directory. It also integrates with subdirectory Makefiles for ipset and IPVS and with architecture/runtime features such as x86 AVX2 and retpoline. Externally, its module names are loaded by userspace tools and kernel module autoload paths, so object renames or symbol mismatches can break runtime firewall tools.

## Risks

Missing an object in a composite module can produce link-time undefined symbols or runtime missing functionality. Adding an object under the wrong symbol can build code without required dependencies. The BTF conditional handling is subtle because module and built-in builds use different debug symbols. Architecture-specific nftables acceleration must avoid unsupported builds, which is why the AVX2 object is guarded by both x86_64 and not UML.

## Test Signals

Useful tests include `make M=net/netfilter`, `make allmodconfig`, `make allyesconfig`, `make randconfig`, and explicit module load tests for `nf_conntrack`, `nf_nat`, `nf_tables`, xtables matches, `ip_set`, and `nf_hooks_lwtunnel`. Build logs should show no orphaned Kconfig symbols or missing object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/core.c -->
# sources/distributed-fs/ceph-client/net/netfilter/core.c

## Purpose

`core.c` implements the central netfilter hook registry and slow-path verdict execution. It manages per-network-namespace hook arrays for IPv4, IPv6, ARP, bridge, netdev ingress/egress, and inet ingress, exposes registration APIs used by protocol modules, and initializes per-net netfilter state and procfs directories.

## Important APIs And Types

Important exports include `nf_register_net_hook`, `nf_unregister_net_hook`, `nf_register_net_hooks`, `nf_unregister_net_hooks`, `nf_hook_entries_insert_raw`, `nf_hook_entries_delete_raw`, `nf_hook_slow`, and `nf_hook_slow_list`. It also exports hook indirection pointers such as `nfnl_ct_hook`, `nf_ct_hook`, `nf_defrag_v4_hook`, `nf_defrag_v6_hook`, and, when conntrack is enabled, `nf_nat_hook`, `nf_ct_attach`, `nf_conntrack_destroy`, `nf_ct_set_closing`, `nf_ct_get_tuple_skb`, and `nf_ct_zone_dflt`.

The core data structure is `struct nf_hook_entries`, a compact allocation containing hook entries, original `nf_hook_ops` pointers, and an RCU head. `nf_hook_mutex` serializes hook table replacement. `dummy_ops` and `accept_all()` are used during unregistration so removing a hook cannot fail while concurrent readers still traverse the old array. With `CONFIG_JUMP_LABEL`, `nf_hooks_needed[NFPROTO_NUMPROTO][NF_MAX_HOOKS]` is exported as static keys for fast hook-presence checks.

## Control Flow

Hook registration calls `nf_register_net_hook`, which expands `NFPROTO_INET` into IPv4 and IPv6 registration except for `NF_INET_INGRESS`. `__nf_register_net_hook` validates netdev/ingress/egress constraints, finds the correct per-net or per-device hook head with `nf_hook_entry_head`, creates a priority-sorted replacement array with `nf_hook_entries_grow`, publishes it with `rcu_assign_pointer`, updates ingress/egress queue counters and jump labels, and frees the old array after RCU.

Unregistration marks the matching entry as `dummy_ops` through `nf_remove_net_hook`, decrements static keys and queue counters, then tries to shrink the array with `__nf_hook_entries_try_shrink`. If all hooks are removed the hook head becomes `NULL`; otherwise a new compact array is published. Queued packets are dropped with `nf_queue_nf_hook_drop` before the old table is released.

`nf_hook_slow` iterates from a supplied hook index. `NF_ACCEPT` continues, `NF_DROP` frees the skb and returns an error, `NF_QUEUE` delegates to `nf_queue`, `NF_STOLEN` returns ownership-derived status, and unexpected verdicts warn and stop. `nf_hook_slow_list` applies the same path to skb lists and rebuilds a list of accepted packets.

## State And Persistence

Hook tables are per network namespace in `net->nf.*` and per device for netdev ingress/egress. Updates are copy-on-write plus RCU; readers can traverse without taking `nf_hook_mutex`. Procfs state is created under each namespace at `net/netfilter` when `CONFIG_PROC_FS` is enabled. There is no disk persistence, but hook registration state persists for the lifetime of modules, namespaces, and devices.

## Dependencies And Integration

The file depends on core networking, net namespaces, RCU, skbuff handling, netdevices, nfqueue, procfs, jump labels, and optional conntrack/NAT. It is consumed by IPv4/IPv6 netfilter paths, nf_tables, xtables, BPF netfilter links, lwtunnel support, conntrack, defragmentation modules, and queue/logging backends.

## Risks

Hook ordering and RCU lifetime are the main risks. `nf_hook_entries_grow` enforces sorted priority order and disallows duplicate-priority BPF hooks, so changes here can reorder packet policy. Unregistration must not fail; replacing hooks with `dummy_ops` avoids allocation failure but requires careful shrink logic. Device namespace checks prevent hooks from attaching to the wrong namespace. Missing static key updates can leave fast paths disabled or incorrectly hot. Verdict handling must preserve skb ownership exactly.

## Test Signals

Signals include module load/unload loops for hooks, nf_tables and xtables rule insertion/removal, BPF hook attach attempts with duplicate priorities, ingress and egress rule tests on netdevices, namespace creation/destruction, nfqueue verdict paths, conntrack/NAT module unload, KASAN/KCSAN/lockdep runs, and packet tests verifying accepted, dropped, queued, and stolen verdict behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/Kconfig -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/Kconfig

## Purpose

This Kconfig file defines the IP set subsystem and its set-type modules. IP set lets userspace create named sets and lets netfilter rules match or update those sets through the `set` match and `SET` target.

## Important Symbols

`IP_SET` is a tristate menuconfig depending on `INET && NETFILTER` and selecting `NETFILTER_NETLINK`, because `ip_set_core.c` registers an nfnetlink subsystem. `IP_SET_MAX` is an integer with default `256` and range `2..65534`; it becomes the default maximum per-network-namespace set count, overridable by the `ip_set` module parameter `max_sets`.

The bitmap set types are `IP_SET_BITMAP_IP`, `IP_SET_BITMAP_IPMAC`, and `IP_SET_BITMAP_PORT`. The hash types include `IP_SET_HASH_IP`, `IP_SET_HASH_IPMARK`, `IP_SET_HASH_IPPORT`, `IP_SET_HASH_IPPORTIP`, `IP_SET_HASH_IPPORTNET`, `IP_SET_HASH_IPMAC`, `IP_SET_HASH_MAC`, `IP_SET_HASH_NETPORTNET`, `IP_SET_HASH_NET`, `IP_SET_HASH_NETNET`, `IP_SET_HASH_NETPORT`, and `IP_SET_HASH_NETIFACE`. `IP_SET_LIST_SET` enables ordered unions of other sets.

## Control Flow And State

All set-type symbols are nested under `if IP_SET`, so no type module is visible unless the core subsystem is enabled. The chosen symbols drive which type modules are compiled by the ipset Makefile. Runtime state is owned by the modules, not Kconfig, but the selected values persist in `.config` and determine what `ipset(8)` can create or autoload.

## Dependencies And Integration

This file integrates with `net/netfilter/Kconfig` through its `source` line, with `ipset/Makefile` through symbol-to-object mappings, with userspace `ipset(8)`, and with xtables/nftables consumers that reference set names and indexes. Every type depends on `IP_SET` and therefore inherits nfnetlink availability.

## Risks

The primary risk is a mismatch between configured type modules and userspace expectations. A deployment may support the core IP set API but fail to create a specific set family if its symbol is off. Another risk is raising or lowering `IP_SET_MAX`: too low can break rule restore workloads, while too high increases possible per-net allocation and lookup surface.

## Test Signals

Use build tests for `CONFIG_IP_SET=y` and `m`, plus per-type module builds. Runtime smoke tests should create, add, test, list, flush, rename, swap, and destroy representative bitmap, hash, and list sets through `ipset(8)`, then exercise xtables rules that match those sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/Makefile -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/Makefile

## Purpose

This Makefile builds the IP set core and selected set-type modules. It is intentionally compact because most type behavior is in individual modules and generic template headers.

## Important Build Rules

`ip_set-y := ip_set_core.o ip_set_getport.o pfxlen.o` builds the core `ip_set` module from the nfnetlink management code, layer-4 port extraction helpers, and prefix-length helpers. `obj-$(CONFIG_IP_SET) += ip_set.o` emits the core. Bitmap modules map directly to `ip_set_bitmap_ip.o`, `ip_set_bitmap_ipmac.o`, and `ip_set_bitmap_port.o`.

Hash modules map to their configured type objects, including `ip_set_hash_ip.o`, `ip_set_hash_ipmac.o`, `ip_set_hash_ipmark.o`, `ip_set_hash_ipport.o`, `ip_set_hash_ipportip.o`, `ip_set_hash_ipportnet.o`, `ip_set_hash_mac.o`, `ip_set_hash_net.o`, `ip_set_hash_netport.o`, `ip_set_hash_netiface.o`, `ip_set_hash_netnet.o`, and `ip_set_hash_netportnet.o`. `IP_SET_LIST_SET` builds `ip_set_list_set.o`.

## Control Flow And State

Kbuild evaluates `obj-$(CONFIG_...)` to decide which objects are built in or modular. There is no runtime state in the Makefile, but it defines the module boundaries used by module autoloading. The core module always includes `ip_set_getport.o`, even if a port-specific set type is not selected, because exported helpers may be shared by configured types.

## Dependencies And Integration

The file must match `ipset/Kconfig` and the source files present in the directory. It integrates with the parent netfilter Makefile through `obj-$(CONFIG_IP_SET) += ipset/` and with module aliases in each type source, such as `ip_set_hash:ip` or `ip_set_bitmap:port`.

## Risks

A missing build mapping makes a configured type unavailable. A stale mapping causes build failures if a source file is moved or removed. Because `ip_set-y` composes the core module, adding shared helpers without updating this list can create unresolved symbols in type modules.

## Test Signals

Build with all ipset options as modules and built-ins. Confirm `modprobe ip_set`, `modprobe ip_set_hash_ip`, `modprobe ip_set_bitmap_ip`, and related aliases work. Runtime `ipset create` commands for every configured type should trigger module loading and successful nfnetlink type registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_gen.h -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_gen.h

## Purpose

`ip_set_bitmap_gen.h` is a C template used by concrete bitmap set modules. A module defines `MTYPE` and type-specific callbacks, includes this header, and receives a complete `struct ip_set_type_variant` with add, delete, test, list, flush, destroy, head, garbage collection, and extension handling.

## Important APIs And Types

The header token-pastes names such as `mtype_add`, `mtype_del`, `mtype_test`, `mtype_list`, `mtype_gc`, and `mtype_variant`. It expects a concrete map type with `members`, `elements`, optional `extensions`, optional `gc`, and a `set` backpointer. Concrete modules provide `mtype_do_test`, `mtype_do_add`, `mtype_do_del`, `mtype_do_list`, `mtype_do_head`, `mtype_kadt`, `mtype_uadt`, and `mtype_same_set`. `IP_SET_BITMAP_STORED_TIMEOUT` enables special handling for set types that can store timeout values before an element is fully active.

## Control Flow

`mtype_add` checks whether the type-specific add reports an existing element, a re-add, or a stored-timeout transition, then initializes timeout, counter, comment, and skbinfo extensions before setting the membership bit and incrementing `set->elements`. `mtype_del` clears membership through the type callback, destroys extensions, decrements the element count, and treats an expired timeout as already absent.

`mtype_test` first checks the membership bit through the type callback, then uses `ip_set_match_extensions` to enforce timeout, counters, counter-match flags, and skbinfo output. `mtype_list` iterates member IDs from the netlink callback cursor, skips absent and expired entries, emits type-specific data, and appends extensions. `mtype_gc` is timer based: it locks the set, scans all possible IDs, clears expired entries, destroys extensions, and reschedules itself. `mtype_head` emits range metadata from the concrete type plus references, memory size, element count, and flags.

## State And Persistence

The bitmap state is in an in-memory bitset plus per-element extension storage. The template mutates `set->elements` and `set->ext_size`. Timeout GC is a kernel timer. There is no disk persistence; state is recreated from userspace commands or restore files.

## Dependencies And Integration

The template depends on `ip_set_core.c` exports for allocation, extension matching, extension serialization, timeout helpers, comments, counters, and flags. It is included by bitmap IP, bitmap IP/MAC, and bitmap port modules. It assumes callers hold the set lock for mutating ADT operations, which the core enforces for userspace and kernel add/delete paths.

## Risks

Because this is macro-generated code, each including module must satisfy the expected callback and data layout contract. Extension offsets are pointer arithmetic over flexible storage, so incorrect `set->dsize` or element alignment in a concrete module can corrupt state. Timeout handling differs when `IP_SET_BITMAP_STORED_TIMEOUT` is set, making partially filled elements a special risk. Listing must maintain the callback cursor correctly or netlink dumps can loop or omit entries.

## Test Signals

Test add/delete/test/list/flush/destroy with and without timeout, counters, comments, and skbinfo for every bitmap type. Exercise expired entries, re-add with `-exist`, list buffer exhaustion, and module unload after active timeout timers. KASAN and lockdep are useful for extension layout and timer lifetime bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_ip.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_ip.c

## Purpose

`ip_set_bitmap_ip.c` implements the `bitmap:ip` IP set type for IPv4 addresses or IPv4 network addresses inside a bounded range. It is efficient for dense, known ranges because membership is a bit indexed by address or subnet offset.

## Important APIs And Types

The module registers `bitmap_ip_type` with name `bitmap:ip`, feature `IPSET_TYPE_IP`, dimension one, family `NFPROTO_IPV4`, and revisions 0 through 3. `struct bitmap_ip` stores the member bitset, first and last IP in host byte order, number of elements, hosts per stored subnet, memory size, netmask, GC timer, set backpointer, and extension storage. `struct bitmap_ip_adt_elem` carries the computed element ID.

Type-specific callbacks include `bitmap_ip_do_test`, `bitmap_ip_do_add`, `bitmap_ip_do_del`, `bitmap_ip_do_list`, `bitmap_ip_do_head`, `bitmap_ip_kadt`, `bitmap_ip_uadt`, and `bitmap_ip_same_set`. Including `ip_set_bitmap_gen.h` generates the variant used by the core.

## Control Flow

Creation requires `IPSET_ATTR_IP` and either `IPSET_ATTR_IP_TO` or `IPSET_ATTR_CIDR`. It normalizes range order, applies optional `IPSET_ATTR_NETMASK`, computes `hosts` and `elements`, rejects ranges larger than `IPSET_BITMAP_MAX_RANGE + 1`, computes extension size with `ip_set_elem_len`, allocates the map plus extension storage, allocates the member bitmap, and starts GC if a timeout was requested.

Kernel ADT extracts the IPv4 source or destination address from the skb, rejects values outside the configured range, converts the IP to an ID with `ip_to_id`, and dispatches to add/delete/test. Userspace ADT parses a single IP, optional `IP_TO` or CIDR range for add/delete, extensions, and then loops by `map->hosts` across the requested range. Test operates on only one address.

## State And Persistence

State is in the bitmap and optional per-entry extension storage. `set->timeout` and the generated GC timer expire elements. `set->family` is fixed to IPv4. There is no persistent storage in the module; userspace must restore sets after reboot.

## Dependencies And Integration

The module depends on ipset prefix helpers, netlink attribute parsing, skb IPv4 address helpers, the bitmap template, and core extension helpers. It integrates with `ipset(8)` through nfnetlink and with xtables/nftables set matching through `kadt`.

## Risks

Range arithmetic is the critical area. Netmask and CIDR normalization must avoid overflow and must reject impossible ranges. Large ranges can consume significant memory, so the `IPSET_BITMAP_MAX_RANGE` check is important. Address zero handling is not globally forbidden here, unlike hash types; tests should confirm intended behavior for ranges including zero. Extension layout must remain aligned with empty `struct bitmap_ip_elem`.

## Test Signals

Create sets from explicit ranges and CIDR ranges, with and without netmask and timeout. Add, delete, test, and list single IPs and ranges; test boundary addresses, reversed ranges, invalid CIDR/netmask, range-size errors, timeout expiry, counters/comments/skbinfo, and packet-path source versus destination matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_ip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_ipmac.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_ipmac.c

## Purpose

`ip_set_bitmap_ipmac.c` implements the `bitmap:ip,mac` set type for IPv4 address and Ethernet MAC pairs over a bounded IPv4 range. It supports a learning-style mode where an IP can be added without a MAC and later completed from packet data.

## Important APIs And Types

The module registers `bitmap_ipmac_type` with name `bitmap:ip,mac`, features `IPSET_TYPE_IP | IPSET_TYPE_MAC`, dimension two, family IPv4, and revisions 0 through 3. `struct bitmap_ipmac` stores the member bitmap, range bounds, element count, memory size, GC timer, set backpointer, and extension storage. `struct bitmap_ipmac_elem` stores `ether[ETH_ALEN]` plus a `filled` state. `MAC_UNSET` means the element exists without a MAC; `MAC_FILLED` means the MAC is known.

`IP_SET_BITMAP_STORED_TIMEOUT` changes generic timeout behavior so an unset-MAC element can store a plain timeout value without starting an active timeout until the MAC is filled.

## Control Flow

Creation parses an IPv4 range or CIDR, rejects ranges larger than `IPSET_BITMAP_MAX_RANGE + 1`, computes an extension layout that includes `struct bitmap_ipmac_elem`, allocates map storage and bitmap, and starts GC when timeout is configured. `ip_to_id` maps an IP directly to `ip - first_ip`.

Kernel ADT validates the skb has an Ethernet device and MAC header, chooses source or destination MAC based on dimension flags, rejects zero MACs, maps the IPv4 address to an ID, and dispatches. Userspace ADT requires an IP and optionally accepts an Ethernet address. If no MAC is provided, add stores a placeholder. Test against a placeholder returns `-EAGAIN`, which the core interprets on packet path as a request to complete the element by performing an add.

The add callback handles four cases: existing filled element, existing unfilled element completed by a MAC, new filled element, and new unfilled element. When replacing a MAC under `IPSET_FLAG_EXIST`, it clears the membership bit before copying because MAC copying is not atomic, then sets the bit through the generic path.

## State And Persistence

State is the range bitmap plus per-entry MAC/fill status and extensions. Timeout values may be inactive plain values for `MAC_UNSET` entries and active jiffies timeouts for `MAC_FILLED` entries. GC only checks filled entries. There is no disk persistence.

## Dependencies And Integration

The module depends on Ethernet header helpers, ARP hardware type constants, IPv4 address extraction, netlink binary attributes, the bitmap template, and ipset core extension functions. It integrates with xtables/nftables packet matching for automatic MAC completion.

## Risks

The special partial-entry state is the main risk. Races around non-atomic MAC updates are mitigated with bit clearing and memory barriers, but changes must preserve that ordering. Timeout semantics differ before and after MAC fill. Packet path operation depends on valid Ethernet headers, so non-Ethernet devices and malformed skbs should fail cleanly. Zero MAC rejection prevents ambiguous elements.

## Test Signals

Test create/add/test/list/delete for IP-only placeholders, IP+MAC entries, timeout completion, `-exist` MAC replacement, source and destination MAC matching, invalid Ethernet attribute lengths, zero MACs, non-Ethernet skb paths, expired filled entries, and list output for unset versus filled entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_ipmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_port.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_port.c

## Purpose

`ip_set_bitmap_port.c` implements the `bitmap:port` set type for a dense range of transport-layer ports. It supports packet-path matching for TCP and UDP over IPv4 or IPv6, while userspace can add, delete, test, and list numeric port ranges.

## Important APIs And Types

The module registers `bitmap_port_type` with name `bitmap:port`, feature `IPSET_TYPE_PORT`, dimension one, family `NFPROTO_UNSPEC`, and revisions 0 through 3. `struct bitmap_port` stores the member bitmap, first/last ports, number of elements, memory size, GC timer, set backpointer, and extension storage. `struct bitmap_port_adt_elem` stores the computed ID.

The local helper `ip_set_get_ip_port` calls `ip_set_get_ip4_port` or `ip_set_get_ip6_port`, then accepts only `IPPROTO_TCP` and `IPPROTO_UDP` for this bitmap type. Common bitmap callbacks handle bit testing, adding, deleting, listing, and header output.

## Control Flow

Creation requires network-order `IPSET_ATTR_PORT` and `IPSET_ATTR_PORT_TO`, optional timeout and create flags, normalizes reversed ranges, computes `elements = last - first + 1`, calculates extension size, allocates map and bitmap, and starts timeout GC if needed.

Kernel ADT extracts the requested source or destination port from the skb based on family and dimension flags. If the protocol is unsupported, the L4 header is unavailable, or the port is outside the configured range, it returns an error. Userspace ADT parses a single port and optional `PORT_TO`, validates the range, parses extensions, and loops over every port for add/delete. Test checks a single port.

## State And Persistence

Membership is a dense bitset indexed by `port - first_port`. Extension state and timeout state are stored in the generic bitmap extension area. `set->family` is unspecified so the same set can serve IPv4 and IPv6 packet paths. There is no persistent kernel storage.

## Dependencies And Integration

The module depends on `ip_set_getport.c` for safe L4 extraction from non-linear skbs, on the bitmap template for ADT implementation, and on ipset core extension helpers. It integrates with packet rules that match source or destination TCP/UDP ports through ipset.

## Risks

The helper accepts only TCP and UDP even though `ip_set_getport.c` can parse SCTP, UDPLITE, and ICMP pseudo-ports. That is intentional for this set type but should be preserved in tests. Range loops use `u32 port` to avoid wraparound but still need boundary coverage around 0 and 65535. Non-linear skb parsing and fragments must fail safely.

## Test Signals

Create sets for small and full port ranges. Add/delete/test individual ports and ranges, including reversed inputs and endpoints 0 and 65535. Exercise TCP and UDP source/destination packet matching for IPv4 and IPv6, unsupported protocols, fragmented packets, timeout expiry, counters, comments, skbinfo, and list output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_core.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_core.c

## Purpose

`ip_set_core.c` implements the core IP set subsystem. It registers set-type modules, manages per-network-namespace set arrays, exposes kernel APIs used by xtables/nftables set consumers, implements the nfnetlink userspace protocol for `ipset(8)`, and provides a legacy getsockopt compatibility interface for iptables/ip6tables.

## Important APIs And Types

Global registries include `ip_set_type_list` protected by `ip_set_type_mutex` and per-set reference counters protected by `ip_set_ref_lock`. `struct ip_set_net` stores the per-net RCU array of set pointers, maximum set count, and deletion/destroy flags. Exported APIs include `ip_set_type_register`, `ip_set_type_unregister`, `ip_set_alloc`, `ip_set_free`, `ip_set_get_ipaddr4`, `ip_set_get_ipaddr6`, `ip_set_init_comment`, `ip_set_extensions`, `ip_set_elem_len`, `ip_set_get_extensions`, `ip_set_put_extensions`, `ip_set_match_extensions`, `ip_set_test`, `ip_set_add`, `ip_set_del`, `ip_set_get_byname`, `ip_set_put_byindex`, `ip_set_name_byindex`, `ip_set_nfnl_get_byindex`, `ip_set_nfnl_put`, and `ip_set_put_flags`.

The nfnetlink subsystem `ip_set_netlink_subsys` dispatches create, destroy, flush, rename, swap, list/save, add, delete, test, header, type, protocol, get-by-name, and get-by-index commands. `so_set` implements legacy `SO_IP_SET` getsockopt operations.

## Control Flow

Type lookup first searches registered types under RCU. If a type is missing, `load_settype` temporarily drops the nfnetlink mutex, calls `request_module("ip_set_%s", name)`, then retries. `ip_set_create` validates the netlink protocol, allocates a base `struct ip_set`, references the type module, parses type-specific creation data, calls the type's `create`, finds or grows a free slot in the per-net set array, and publishes the set.

Destroy is two-stage for single sets: it checks `ref` and `ref_netlink`, removes the set pointer, cancels GC, waits for list-set flushes when needed, then releases through `call_rcu`. Destroy-all cancels all GCs, optionally waits for RCU barriers, then destroys every set. Flush, rename, and swap are serialized by nfnetlink and use set locks or `ip_set_ref_lock` as needed.

Kernel packet APIs fetch the set by index, validate dimensions and family, and call the variant `kadt`. `ip_set_test` treats `-EAGAIN` as a type request to complete an element by adding it, then converts errors to no-match. Userspace add/delete/test parse nested ADT attributes and call `uadt`; `call_ad` handles resize retries, range continuations, and restore-line error reporting.

Dumping uses netlink dump callbacks. It pins the set with `ref_netlink`, asks variants for headers and list elements, supports one-set and all-set dumps, and dumps list-like sets last. Extension helpers parse and serialize timeouts, counters, comments, skbinfo, and counter match operations.

## State And Persistence

All set data is per network namespace and in memory. `max_sets` defaults from `CONFIG_IP_SET_MAX` but can be overridden as a module parameter. Set pointers are RCU-protected, while set references prevent destruction under packet users or netlink dumps. Comments use RCU-allocated strings and contribute to `set->ext_size`. There is no disk persistence; userspace restore is required after reboot.

## Dependencies And Integration

The core depends on nfnetlink, net namespaces, RCU, x_tables action parameters, skbuffs, netlink attributes, module autoloading, and each registered type's variant contract. It integrates with `ip_set_getport.c`, pfxlen helpers, bitmap/hash/list modules, xt_set/SET target users, and `ipset(8)`.

## Risks

Concurrency and lifetime are the main risks. Set arrays are RCU-published and can grow; references must be balanced across packet path, netlink dumps, destroy, and namespace teardown. The nfnetlink mutex serializes userspace structural operations, but kernel packet operations can race resize and destroy. Extension layout is shared with every type, so changes to `ip_set_elem_len` or extension order can corrupt stored elements. Type autoload drops and reacquires locks, so retry paths must be correct. Restore-line error rewriting copies netlink payloads and requires strict bounds handling.

## Test Signals

Exercise all nfnetlink commands, including batch add/delete with line numbers, list/save dumps with small skb sizes, resize retries, set array growth past the initial maximum, module autoload, namespace teardown, legacy getsockopt operations, comments/counters/skbinfo/timeouts, concurrent packet matching during create/destroy/swap/resize, and lockdep/KASAN/KCSAN runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_getport.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_getport.c

## Purpose

`ip_set_getport.c` provides shared helpers for extracting layer-4 port-like values from IPv4 and IPv6 skbs for IP set packet-path matching. It handles non-linear skbs through `skb_header_pointer` and exports IPv4 and IPv6 helpers to set-type modules.

## Important APIs

The internal `get_port` handles TCP, SCTP, UDP, UDPLITE, ICMP, and ICMPv6. For TCP/SCTP/UDP/UDPLITE it returns the selected source or destination port. For ICMP and ICMPv6 it synthesizes a 16-bit value from type and code. It also returns the protocol through `proto`.

`ip_set_get_ip4_port` extracts the IPv4 header, computes the transport offset, rejects invalid protocol values and transport fragments with nonzero offset for protocols where the L4 header is unavailable, and then calls `get_port`. `ip_set_get_ip6_port`, compiled when `CONFIG_IP6_NF_IPTABLES` is enabled, uses `ipv6_skip_exthdr` to locate the final header, rejects non-initial fragments, and calls `get_port`.

## Control Flow And State

Both exported functions are read-only packet parsers. They return `true` when the protocol can be represented and the needed header bytes are available, otherwise `false`. No state is stored and no skb data is modified.

## Dependencies And Integration

The file depends on IPv4/IPv6 headers, ICMP/ICMPv6, SCTP, UDP/TCP header definitions, `skb_header_pointer`, and IPv6 extension-header parsing. It is built into the `ip_set` core module by the ipset Makefile and used by port-bearing set types, including `bitmap:port` in this subset.

## Risks

Fragment and non-linear skb handling are the main risks. Returning a port for a non-initial fragment would allow false matches, while failing to use `skb_header_pointer` would break non-linear skbs. IPv6 extension parsing must reject invalid offsets and fragmented packets where the L4 header is not available. Consumers may further filter accepted protocols, so helper behavior should remain protocol-general.

## Test Signals

Packet tests should cover linear and non-linear skbs, IPv4 fragments with offset zero and nonzero, IPv6 extension headers and fragments, TCP/UDP/SCTP/UDPLITE source and destination extraction, ICMP type/code extraction, unsupported protocols, truncated headers, and builds with and without IPv6 iptables support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_getport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_gen.h -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_gen.h

## Purpose

`ip_set_hash_gen.h` is the generic hash set implementation template used by concrete hash set modules. Including modules define `HTYPE`, `MTYPE`, `HOST_MASK`, element structures, equality/listing helpers, and optional feature macros, and this header generates hash-table storage, add/delete/test/list/head, resize, garbage collection, and create logic.

## Important APIs And Types

The generic storage is `struct htable`, which contains RCU bucket pointers, hash-table size bits, per-region locks and counters, and resize reference counters. `struct hbucket` stores an array of fixed-size element records plus a bitmap of used slots. `struct htype` is token-pasted from `MTYPE` and stores the current RCU table, GC work, max elements, jhash seed, bucket size, optional netmask/bitmask/markmask, a resize add/delete backlog, a `next` cursor for range retries, and optional network prefix bookkeeping.

Generated variant callbacks include `mtype_add`, `mtype_del`, `mtype_test`, `mtype_resize`, `mtype_head`, `mtype_list`, `mtype_flush`, `mtype_destroy`, `mtype_uref`, `mtype_cancel_gc`, and `mtype_same_set`. When `IP_SET_EMIT_CREATE` is defined, the header also generates `HTYPE_create`.

## Control Flow

Add computes a jhash key over the element bytes, selects a region lock, checks region/global limits, optionally runs GC, reuses deleted or expired slots, supports force-add replacement, grows bucket arrays by `AHASH_INIT_SIZE`, and returns `-EAGAIN` to trigger resize when a bucket is full. It initializes counters, comments, skbinfo, and timeouts before marking a slot used. Delete clears the used bit, updates region counters, removes network prefix counts when enabled, destroys extensions, and shrinks or frees sparse buckets.

Resize allocates a table with one more hash bit, rehashes all live non-expired elements under RCU protection, publishes the new table, waits for readers, then replays kernel-side add/delete operations saved in `h->ad` during resize. Old tables are destroyed only when `uref` reaches zero. GC runs as delayed work over one region at a time, removing expired elements and shrinking buckets.

Test either hashes the exact element or, for network-aware types, iterates stored prefix lengths to match host addresses against network entries. Listing pins the table with `mtype_uref`, walks buckets from a netlink cursor, skips expired elements, emits type-specific data and extensions, and handles skb space limits. Head reports hashsize, maxelem, optional bitmask/netmask/markmask, bucket size/initval, references, memory size, element count, and set flags.

## State And Persistence

State is entirely in memory: RCU hash tables, per-region locks/counters, delayed work for timeout GC, element extension storage, prefix counters, and resize backlog entries. The create path accepts userspace `hashsize`, `maxelem`, timeout, bucket size, initval, netmask/bitmask, and flags. There is no persistent storage beyond userspace restore.

## Dependencies And Integration

The template depends on jhash, RCU, nfnetlink lock assertions, delayed work, ipset allocation and extension APIs, netmask helpers, and concrete type helpers. It is included twice by dual-family modules to generate IPv4 and IPv6 variants, with the second include usually defining `IP_SET_EMIT_CREATE`.

## Risks

This is a high-risk concurrency template. Region locking, RCU table replacement, `ref` and `uref` lifetimes, and resize backlog replay must remain consistent. Element size must be a multiple of `u32` for `jhash2`, enforced by `BUILD_BUG_ON`. Optional macros change data layout and matching semantics, so each concrete type must define equality, masking, and listing correctly. Force-add can evict existing elements under pressure. Net prefix bookkeeping must stay synchronized with add, delete, GC, and resize.

## Test Signals

Run hash-type tests with small bucket sizes and low maxelem to force bucket growth, resize, forceadd, GC, and full-set errors. Add concurrent packet-path add/delete/test while userspace triggers resize and dumps. Exercise timeout expiry, comments/counters/skbinfo, netmask/bitmask options, initval reproducibility, bucket-size create flags, net prefix matching, dump resumption after small skb limits, and KASAN/KCSAN/lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ip.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ip.c

## Purpose

`ip_set_hash_ip.c` implements the `hash:ip` set type for arbitrary IPv4 or IPv6 addresses, with optional netmask or bitmask normalization. It is the flexible sparse counterpart to `bitmap:ip`.

## Important APIs And Types

The module registers `hash_ip_type` with name `hash:ip`, feature `IPSET_TYPE_IP`, dimension one, family `NFPROTO_UNSPEC`, revisions 0 through 6, and bucket-size/create-initval support at the latest revision. It enables `IP_SET_HASH_WITH_NETMASK` and `IP_SET_HASH_WITH_BITMASK` before including the hash template.

`struct hash_ip4_elem` stores a nonzero `__be32 ip`. `struct hash_ip6_elem` stores a `union nf_inet_addr ip`. Type helpers implement equality, listing, and range retry cursor updates. Including `ip_set_hash_gen.h` generates separate IPv4 and IPv6 variants plus the shared create routine.

## Control Flow

Kernel IPv4 ADT extracts source or destination IPv4, masks it with `h->bitmask.ip`, rejects zero, and dispatches. Userspace IPv4 ADT parses IP, extensions, optional `IP_TO` range or CIDR, masks values, rejects zero elements, computes `hosts` from the configured netmask, and loops through the range. If more than `IPSET_MAX_RANGE` entries are attempted in one call, it stores the next element in `h->next` and returns `-ERANGE` so core retry logic can reschedule.

Kernel IPv6 ADT extracts and masks the selected IPv6 address, rejects `::`, and dispatches. Userspace IPv6 ADT accepts only a single IPv6 address, rejects `IP_TO`, and only accepts CIDR equal to the host mask; range expansion is not supported for IPv6 in this type. Both families use the generic hash variant for add/delete/test/resize/list/GC.

Creation is generated by the hash template. It validates family, hashsize, maxelem, timeout, create flags, optional netmask, optional bitmask, bucket size, and initval, then selects the IPv4 or IPv6 variant and computes per-element extension size.

## State And Persistence

State is the generic RCU hash table plus optional timeouts and extensions. Netmask/bitmask settings are stored in the set data and emitted in headers. IPv4 range retries use `h->next`. There is no disk persistence.

## Dependencies And Integration

The module depends on IPv4/IPv6 address extraction helpers, ipset prefix/netmask helpers, netlink nested IP attributes, jhash/random seed support, and the generic hash template. It integrates with userspace `ipset create hash:ip` and packet rules matching source or destination IP addresses.

## Risks

Zero-address rejection is important because zero values are reserved as invalid elements. Netmask and bitmask are mutually exclusive in create logic and can silently normalize input; tests must verify listed values match normalized storage. IPv4 range expansion can be expensive and relies on retry handling for large ranges. IPv6 range support is intentionally rejected. Hash resize and timeout behavior inherits the template's concurrency risks.

## Test Signals

Test IPv4 and IPv6 create paths with hashsize, maxelem, timeout, bucket size, initval, netmask, and bitmask. Add/test/delete/list single addresses, IPv4 ranges, CIDR ranges, zero addresses, masked addresses, duplicate adds with and without `-exist`, large ranges that trigger `-ERANGE`, hash resize, timeout GC, and packet-path source/destination matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipmac.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipmac.c

## Purpose

`ip_set_hash_ipmac.c` implements the `hash:ip,mac` set type for sparse IPv4 or IPv6 address plus Ethernet MAC pairs. Unlike `bitmap:ip,mac`, each element requires both IP and MAC data; there is no placeholder MAC learning state.

## Important APIs And Types

The module registers `hash_ipmac_type` with name `hash:ip,mac`, features `IPSET_TYPE_IP | IPSET_TYPE_MAC`, dimension two, family `NFPROTO_UNSPEC`, and revisions 0 through 1. Revision 1 adds bucket-size and initval create support. `struct hash_ipmac4_elem` stores `__be32 ip` and an aligned Ethernet address. `struct hash_ipmac6_elem` stores a `union nf_inet_addr ip` and an aligned Ethernet address. `HKEY_DATALEN` is set to the full element size for both families so the hash key covers IP and MAC bytes.

The concrete helpers provide equality over both IP and MAC, netlink listing of IP and Ethernet attributes, and range cursor placeholders. The hash template generates IPv4 and IPv6 variants and the shared create routine.

## Control Flow

Kernel ADT validates that the skb is on an Ethernet device, that a MAC header is set and long enough, chooses source or destination MAC according to the second dimension flag, rejects zero MACs, extracts source or destination IP according to the first dimension flag, and dispatches to the generated add/delete/test callback.

Userspace IPv4 ADT requires nested IP and binary Ethernet attributes, validates all optional extension attributes have network byte order, parses the IPv4 address and extensions, copies the MAC, rejects zero MACs, and dispatches. IPv6 follows the same pattern using `ip_set_get_ipaddr6`. No userspace IP ranges are implemented; each ADT call handles one IP/MAC pair.

Creation is generated by the hash template and supports hashsize, maxelem, timeout, create flags, bucket size, resize, and initval. Since this type does not define netmask or bitmask macros, addresses are stored exactly as provided.

## State And Persistence

State is the generic hash table and per-element extensions. Each element is keyed by full IP+MAC data. Timeouts use delayed work from the hash template when configured. The module has no disk persistence and no partially filled element state.

## Dependencies And Integration

The module depends on Ethernet header helpers, IPv4/IPv6 packet address helpers, netlink IP parsing, binary MAC attributes, random jhash seed support, and the generic hash template. It integrates with `ipset(8)` and packet-path set rules that use two dimensions.

## Risks

Packet-path validation must reject non-Ethernet devices, missing MAC headers, truncated headers, and zero MACs. Element struct padding matters because `HKEY_DATALEN` covers the whole element; the union with `foo[2]` aligns the MAC area and reduces undefined padding concerns. Userspace policy for `IPSET_ATTR_COMMENT` lacks an explicit max length in this file, so core/comment handling must still cap stored comments. Hash template resize and lifetime risks apply.

## Test Signals

Test IPv4 and IPv6 add/delete/test/list for source and destination MAC modes, zero MAC rejection, missing Ethernet header rejection, non-Ethernet devices, duplicate adds with and without `-exist`, timeout expiry, comments/counters/skbinfo, bucket-size/initval create options, hash resize, module load/unload, and packet matching for both address families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipmac.c -->
