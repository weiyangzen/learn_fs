# subset-b-006188 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/xdp.c -->
# sources/distributed-fs/ceph-client/net/core/xdp.c

## Purpose

`xdp.c` implements core XDP runtime support shared by network drivers, AF_XDP, page-pool backed receive queues, skb conversion, metadata kfunc registration, and netdev XDP feature notifications. It is not a packet program runner; it manages the memory and object plumbing that lets drivers safely hand buffers to XDP and later recycle or convert them.

## Important APIs, Types, and Functions

The receive-queue registration API is `__xdp_rxq_info_reg()`, `xdp_rxq_info_unreg()`, `xdp_rxq_info_reg_mem_model()`, `xdp_rxq_info_unreg_mem_model()`, `xdp_rxq_info_unused()`, and `xdp_rxq_info_is_reg()`. Memory-provider registration is handled through `xdp_reg_mem_model()`, `xdp_reg_page_pool()`, `xdp_unreg_page_pool()`, and `xdp_rxq_info_attach_page_pool()`, with provider IDs tracked by `struct xdp_mem_allocator`, `mem_id_pool`, and `mem_id_ht`. Buffer return paths include `__xdp_return()`, `xdp_return_frame()`, `xdp_return_frame_rx_napi()`, `xdp_return_frame_bulk()`, `xdp_return_frag()`, and `xdp_return_buff()`. Conversion helpers include `xdp_convert_zc_to_xdp_frame()`, `xdp_build_skb_from_buff()`, `xdp_build_skb_from_zc()`, `__xdp_build_skb_from_frame()`, `xdp_build_skb_from_frame()`, and `xdpf_clone()`. The BPF metadata kfunc stubs are `bpf_xdp_metadata_rx_timestamp()`, `bpf_xdp_metadata_rx_hash()`, and `bpf_xdp_metadata_rx_vlan_tag()`.

## Control Flow

Drivers register `struct xdp_rxq_info` before exposing queues to XDP, optionally bind an XDP memory model, and unregister during teardown. Page-pool backed memory gets a cyclic ID, an rhashtable entry, and a page-pool disconnect callback. When a page pool disconnects, `mem_allocator_disconnect()` walks the ID table under `mem_id_lock` and removes matching allocators; removal frees IDs after an RCU grace period. XDP frame return dispatches by `enum xdp_mem_type`, with page-pool paths optionally using NAPI direct recycling and bulk queues. skb conversion either wraps existing XDP frame memory or allocates/copies from zero-copy XSK buffers when ownership cannot be transferred directly. Metadata kfuncs default to `-EOPNOTSUPP`; drivers can provide device-bound implementations through BTF kfunc dispatch. Feature setters update `dev->xdp_features` under netdev locking and notify listeners when registered devices change capabilities.

## State and Persistence Behavior

Persistent global state is the lazily allocated memory-ID rhashtable, IDA allocator, cyclic `mem_id_next`, and metadata BTF kfunc registration. Per-queue state lives in `struct xdp_rxq_info`: registration state, device pointer, queue index, fragment size, and memory info. Page pools retain `xdp_mem_id` ownership until unregistered or disconnected. Feature bits persist in `net_device::xdp_features`. RCU protects allocator lookup/free, while `mem_id_lock` serializes registration, cyclic ID allocation, and disconnect walks.

## Dependencies and Integration Points

The file integrates with page_pool, AF_XDP buffer pools, BPF/BTF kfunc infrastructure, netdevice locking/notifiers, skb allocation/build helpers, tracepoints, and NAPI recycling. Drivers call the exported GPL symbols to register queues and memory models. The skb conversion helpers are used when XDP actions pass packets into the normal networking stack.

## Risks

The high-risk area is lifetime management across page-pool disconnect, rhashtable lookup, RCU free, and ID reuse. `xdp_unreg_mem_model()` assumes the ID lookup succeeds for page pools before `page_pool_destroy()`. Incorrect `mem_type` propagation can free memory through the wrong allocator. skb conversion must preserve metadata, frags, truesize, pfmemalloc flags, and recycle eligibility. Feature updates must hold the expected netdev lock or notify listeners from inconsistent state. XSK zero-copy conversion is copy-heavy and must leave ownership unchanged on allocation failure.

## Test Signals

Useful coverage includes driver queue register/unregister misuse warnings, page-pool register/unregister and disconnect callbacks, cyclic ID wrap, XDP frame returns for page-pool, order-0, shared page, and XSK memory, fragmented XDP frames, skb conversion with metadata and frags, BPF metadata kfunc fallback behavior, and XDP feature-change notifier delivery. KASAN/KCSAN/lockdep runs are valuable for allocator lifetime and lock-order issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dcb/Kconfig -->
# sources/distributed-fs/ceph-client/net/dcb/Kconfig

## Purpose

This Kconfig entry exposes `CONFIG_DCB`, the build-time option for Data Center Bridging rtnetlink support. It describes DCB as Ethernet enhancements for mixed traffic requirements and lists Enhanced Transmission Selection and Priority-based Flow Control as key features.

## Important APIs, Types, and Functions

There are no runtime APIs in this file. The important symbol is `DCB`, a boolean option defaulting to `n`. Enabling it causes the DCB net subsystem objects from this directory to be built according to the parent networking Makefiles.

## Control Flow

The file participates only in Kconfig resolution. When selected by a user or another config dependency, code guarded by `CONFIG_DCB` becomes available and the `net/dcb` objects can provide rtnetlink handling and notifier APIs.

## State and Persistence Behavior

The only state is the kernel build configuration. It persists in `.config` and determines whether DCB code is compiled into the kernel image.

## Dependencies and Integration Points

The option is presented to networking configuration users and is consumed by the kernel build system. Its help text targets DCB-capable Ethernet adapters and switches.

## Risks

Because the option defaults off, driver or distribution configs that expect DCB must explicitly enable it or select it. The help text is descriptive but does not encode dependencies, so dependency correctness must be maintained outside this file.

## Test Signals

Build tests should cover `CONFIG_DCB=y` and `CONFIG_DCB=n`, confirming that DCB rtnetlink handlers and exported notifier/app APIs appear only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dcb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dcb/Makefile -->
# sources/distributed-fs/ceph-client/net/dcb/Makefile

## Purpose

The DCB Makefile defines the objects that make up the Data Center Bridging networking support directory.

## Important APIs, Types, and Functions

It builds `dcbnl.o` and `dcbevent.o` into the directory object through `obj-y`.

## Control Flow

At build time, Kbuild compiles and links the DCB rtnetlink implementation and event notifier implementation whenever the enclosing DCB directory is included by configuration.

## State and Persistence Behavior

There is no runtime state. The file influences build artifact composition only.

## Dependencies and Integration Points

`dcbnl.o` provides rtnetlink command handling and exported DCB app helpers. `dcbevent.o` provides the notifier chain used by DCB app change notifications. Both integrate with the broader networking build.

## Risks

Adding new DCB source files without updating this Makefile would omit runtime functionality. Removing one of these objects would break either user-facing netlink configuration or internal DCB event delivery.

## Test Signals

Build with DCB enabled and verify both `dcbnl_init()` and the dcbevent exported symbols are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dcb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dcb/dcbevent.c -->
# sources/distributed-fs/ceph-client/net/dcb/dcbevent.c

## Purpose

`dcbevent.c` implements the small exported DCB event notification bus. It lets DCB users register notifier blocks and lets DCB core code broadcast events such as application-priority mapping changes.

## Important APIs, Types, and Functions

The public functions are `register_dcbevent_notifier()`, `unregister_dcbevent_notifier()`, and `call_dcbevent_notifiers()`. They operate on the file-local `ATOMIC_NOTIFIER_HEAD(dcbevent_notif_chain)`.

## Control Flow

Consumers register a `struct notifier_block` into the atomic notifier chain. DCB code calls `call_dcbevent_notifiers(val, v)` with an event ID and event payload. The notifier core invokes registered callbacks in priority order and returns the aggregate notifier result.

## State and Persistence Behavior

The notifier chain is global kernel state for the lifetime of the DCB subsystem. It stores registered notifier blocks but does not own their memory; callers must unregister before freeing their blocks.

## Dependencies and Integration Points

The file depends on Linux notifier APIs and exports its functions for other kernel modules. `dcbnl.c` calls `call_dcbevent_notifiers(DCB_APP_EVENT, &event)` after successful APP table changes.

## Risks

The chain is atomic, so notifier callbacks must obey atomic notifier constraints and avoid sleeping where not allowed. Lifetime bugs occur if a module frees a notifier block without unregistering it.

## Test Signals

Tests should register multiple notifier blocks, trigger DCB app changes, verify callback ordering and payload content, and validate clean unregister paths during module/device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dcb/dcbevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dcb/dcbnl.c -->
# sources/distributed-fs/ceph-client/net/dcb/dcbnl.c

## Purpose

`dcbnl.c` implements the Data Center Bridging rtnetlink interface and the kernel-side DCB application and rewrite tables. It supports legacy CEE DCBX commands, IEEE 802.1Qaz/Qau/Qbb attributes, PFC, ETS/priority groups, BCN, DCBX mode, feature config, application trust, and helper APIs that drivers and upper layers use to query or mutate DCB app mappings.

## Important APIs, Types, and Functions

The file defines netlink policy tables for top-level DCB attributes and nested PFC, PG, TC, capability, NUMTCS, BCN, APP, IEEE, and feature-config attributes. Main request handlers include `dcbnl_getstate()`, `dcbnl_setstate()`, `dcbnl_getpfccfg()`, `dcbnl_setpfccfg()`, `dcbnl_getcap()`, `dcbnl_getnumtcs()`, `dcbnl_setnumtcs()`, `dcbnl_getapp()`, `dcbnl_setapp()`, priority-group handlers, BCN handlers, `dcbnl_ieee_get()`, `dcbnl_ieee_set()`, `dcbnl_ieee_del()`, `dcbnl_getdcbx()`, `dcbnl_setdcbx()`, feature handlers, and `dcbnl_cee_get()`. Exported data APIs include `dcb_getapp()`, `dcb_setapp()`, `dcb_ieee_getapp_mask()`, `dcb_ieee_setapp()`, `dcb_ieee_delapp()`, `dcb_getrewr()`, `dcb_setrewr()`, `dcb_delrewr()`, DSCP/PCP mapping helpers, and default-priority lookup.

## Control Flow

`dcb_doit()` is the rtnetlink entry point for `RTM_GETDCB` and `RTM_SETDCB`. It checks capabilities for set operations, parses attributes, finds the target device by `DCB_ATTR_IFNAME`, validates `dev->dcbnl_ops`, allocates a reply, and dispatches through `reply_funcs[dcb->cmd]`. Most handlers parse a nested attribute set, call optional driver callbacks from `struct dcbnl_rtnl_ops`, and encode a reply or status byte. IEEE set/delete paths can also fall back to the file's software APP and rewrite tables when driver-specific callbacks are absent. Notification helpers build IEEE or CEE snapshots and multicast them on `RTNLGRP_DCB`.

## State and Persistence Behavior

The persistent state owned here is `dcb_app_list`, `dcb_rewr_list`, and `dcb_lock`. Entries are keyed by netdevice ifindex plus selector/protocol/priority depending on APP versus rewrite semantics. CEE `dcb_setapp()` replaces an existing selector/protocol mapping or deletes it when priority is zero. IEEE `dcb_ieee_setapp()` permits multiple priorities for the same selector/protocol. Rewrite entries require selector/priority/protocol uniqueness. Device unregister triggers `dcbnl_flush_dev()`, which clears APP entries for the ifindex; rewrite entries are not flushed in this function. Successful APP mutations broadcast `DCB_APP_EVENT` through `dcbevent`.

## Dependencies and Integration Points

The file integrates with rtnetlink, generic netlink attribute helpers, netdevice lookup/notifiers, `struct dcbnl_rtnl_ops` supplied by drivers, and `dcbevent.c`. It exports helper APIs used by classifiers, VLAN/DSCP logic, and drivers that need app-priority maps. Initialization registers netdevice and rtnetlink handlers with `device_initcall()`.

## Risks

Netlink handlers have many optional driver callbacks; missing callback checks must remain complete to avoid NULL calls. Several setters perform multiple driver operations without rollback, matching the file comment that partial success is not reconciled. Attribute validation is especially important for app selector/type matching and app trust duplicate detection. Global APP/rewrite tables are ifindex based, so stale entries on unregister or ifindex reuse are a risk, particularly for rewrite entries. Message construction has many nested attributes and must cancel nests on `-EMSGSIZE` to avoid malformed replies.

## Test Signals

Exercise all DCB commands through rtnetlink with supported and unsupported driver callbacks, malformed nested attributes, non-admin set attempts, IEEE APP add/delete, CEE priority-zero delete, duplicate APP and rewrite entries, app trust selector validation, DCBX mode changes, device unregister cleanup, and multicast notification contents. Lockdep and fault-injection tests around `kmalloc_obj()` and skb size failures are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dcb/dcbnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/Makefile -->
# sources/distributed-fs/ceph-client/net/devlink/Makefile

## Purpose

This Makefile defines the object set for the devlink subsystem.

## Important APIs, Types, and Functions

It links `core.o`, `netlink.o`, generated netlink ops, and feature modules for devices, ports, shared buffers, dpipe, resources, params, regions, health, traps, rates, linecards, and shared devlink support.

## Control Flow

Kbuild compiles the listed objects into the devlink directory object. The ordering ensures the core and netlink implementation are present together with all built-in devlink feature providers.

## State and Persistence Behavior

There is no runtime state in this file. Runtime state is in the C objects it selects.

## Dependencies and Integration Points

The object list reflects devlink's modular internal structure. `netlink_gen.o` supplies generated split operation tables consumed by `netlink.c`, while the other files implement handlers referenced by those tables.

## Risks

Any mismatch between generated netlink operations and linked handler objects can cause build failures. Omitting a feature object would silently remove handler implementations from the subsystem.

## Test Signals

Build tests should verify all devlink objects compile together after generated netlink changes and that no handler referenced by `netlink_gen.o` is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/core.c -->
# sources/distributed-fs/ceph-client/net/devlink/core.c

## Purpose

`core.c` owns devlink instance allocation, registration, reference counting, global lookup, namespace exit handling, nested devlink relationships, lock helpers, and tracepoint exports. It is the foundation used by all devlink feature modules and generated netlink handlers.

## Important APIs, Types, and Functions

Global state is `DEFINE_XARRAY_FLAGS(devlinks, XA_FLAGS_ALLOC)` and the private `devlink_rels` xarray. Public helpers include `devlink_priv()`, `priv_to_devlink()`, `devlink_to_dev()`, `devlink_bus_name()`, `devlink_dev_name()`, `devlink_dev_driver_name()`, `devlink_net()`, `devl_lock()`, `devl_trylock()`, `devl_unlock()`, `devlink_try_get()`, `devlink_put()`, `devl_register()`, `devlink_register()`, `devl_unregister()`, `devlink_unregister()`, `devlink_alloc_ns()`, and `devlink_free()`. Relationship APIs are `devlink_rel_nested_in_add()`, `devlink_rel_nested_in_clear()`, `devlink_rel_nested_in_notify()`, and `devlink_rel_devlink_handle_put()`.

## Control Flow

Allocation validates reload ops, allocates a flexible `struct devlink`, assigns a cyclic xarray index, stores either a device reference or synthetic index name, initializes all child collections, sets the network namespace, creates the instance mutex, and initializes refcounting. Registration marks the xarray slot with `DEVLINK_REGISTERED`, sends notifications, and notifies parent relationships. Lookup uses RCU plus `devlink_try_get()` and then callers lock the instance before trusting registration. Unregister clears the registered mark after sending delete notifications and tears down nested relationships. Final free asserts child collections are empty, destroys xarrays, removes the global slot, and drops the last reference, which queues RCU work for memory release.

## State and Persistence Behavior

Devlink instances persist in the global xarray until `devlink_free()`. A reference only guarantees the object can be locked; registration must be checked separately under the devlink lock. Nested relationships persist as `struct devlink_rel` entries with refcounts and delayed work so parent notifications can be sent without assuming parent lock state. Network namespace pre-exit reloads registered devlinks into `init_net` when possible.

## Dependencies and Integration Points

The file registers the devlink generic netlink family, pernet pre-exit hook, and netdevice notifier at `subsys_initcall()`. It relies on `devl_internal.h` definitions and callback functions implemented in other devlink modules for port notification, reload validation, params, resources, rates, and linecards.

## Risks

Registration state, refcounting, and locking are tightly coupled. A caller that treats a reference as proof of registration can race unregister. Relationship delayed work must handle parent lock contention and stale relationship cleanup correctly. `devlink_free()` depends on drivers unregistering all child objects first. Namespace pre-exit reload failures can leave warnings and require driver reload correctness.

## Test Signals

Test allocation/register/unregister/free with child objects present and absent, concurrent netlink lookup during unregister, nested devlink attach/detach notifications, namespace teardown reload, lockdep assertions, and fault injection in xarray allocation or synthetic-name allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/dev.c -->
# sources/distributed-fs/ceph-client/net/devlink/dev.c

## Purpose

`dev.c` implements top-level devlink device netlink operations and helper APIs: instance dumps, reload, nested devlink reporting, eswitch configuration, device info/version reporting, firmware flash update, compatibility helpers, and selftests.

## Important APIs, Types, and Functions

Key handlers include `devlink_nl_get_doit()`, `devlink_nl_get_dumpit()`, `devlink_nl_reload_doit()`, `devlink_nl_eswitch_get_doit()`, `devlink_nl_eswitch_set_doit()`, `devlink_nl_info_get_doit()`, `devlink_nl_info_get_dumpit()`, `devlink_nl_flash_update_doit()`, `devlink_nl_selftests_get_doit()`, `devlink_nl_selftests_get_dumpit()`, and `devlink_nl_selftests_run_doit()`. Exported helpers include `devl_nested_devlink_set()`, `devlink_is_reload_failed()`, `devlink_remote_reload_actions_performed()`, `devlink_info_*_put()`, `devlink_flash_update_status_notify()`, `devlink_flash_update_timeout_notify()`, `devlink_compat_running_version()`, and `devlink_compat_flash_update()`.

## Control Flow

Device GET fills the devlink handle, reload failure bit, local and remote reload stats, and nested devlink handles. Register/unregister notification fans out to linecards, ports, traps, rates, regions, and params in a defined order. Reload validates resources, requested action, limit, and optional target namespace, then calls driver `reload_down()`, changes namespace if requested, reloads driverinit params and sanity-checks empty reinit-only object lists for driver reinit, calls `reload_up()`, updates failure state, verifies actions performed, and increments stats. Flash update validates optional component support by probing `info_get()` versions, requests firmware, emits begin/end/status notifications, and calls driver `flash_update()`. Selftests advertise supported test IDs and run selected tests with per-test result attributes.

## State and Persistence Behavior

Persistent devlink state touched here includes `reload_failed`, local and remote reload stat arrays, nested relationship xarray entries, net namespace pointer, and driverinit parameter state. Firmware pointers are transient and released after flash update. Info reporting is callback driven and stateless except for optional version callback collection used for component validation and compatibility running-version strings.

## Dependencies and Integration Points

The file depends on `struct devlink_ops` callbacks for reload, eswitch, info, flash, and selftests. It integrates with net namespace lookup/capability checks, firmware loader, generic netlink replies and multicast notifications, devlink resources, params, rates, and nested relationship support from `core.c`.

## Risks

Reload is sensitive because it may change namespaces and expects device lock ownership. Drivers must report performed actions consistently and must not update remote stats during local reload. Flash update component validation depends on version names and types reported by `info_get()`. Selftest run previously parsed nested requested flags; missing attribute checks can lead to unexpected skips. Notification order matters for userspace object tracking.

## Test Signals

Test reload with default and explicit action/limit, invalid action-limit combinations, namespace moves, reload failure state toggling, remote reload stat updates, eswitch get/set with absent callbacks, info version nesting, flash firmware lookup and unsupported component errors, overwrite mask support, compatibility flash path, and selftest get/run skip/pass/fail statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/devl_internal.h -->
# sources/distributed-fs/ceph-client/net/devlink/devl_internal.h

## Purpose

`devl_internal.h` is the private header tying the devlink implementation together. It defines the internal `struct devlink`, shared state structures, lock and registration assertions, netlink dump state, notification helpers, and cross-module prototypes.

## Important APIs, Types, and Functions

The central type is `struct devlink`, containing the global index, child object collections, ops pointers, namespace, mutex, refcount, RCU work, nested relationship state, reload stats, and private driver storage. Other important definitions are `struct devlink_dev_stats`, `DEVLINK_REGISTERED`, `DEVLINK_RELOAD_STATS_ARRAY_SIZE`, `devlinks_xa_for_each_registered_get`, `devl_dev_lock()`, `devl_dev_unlock()`, `struct devlink_nl_dump_state`, `devlink_nl_put_handle()`, `devlink_nl_put_u64()`, `struct devlink_obj_desc`, and notification send helpers.

## Control Flow

This header supplies inline helpers used by generated netlink handlers and feature modules. Pre-doit code resolves and locks a devlink, handlers use `info->user_ptr`, fill replies with `devlink_nl_put_handle()`, and notifications use `devlink_nl_obj_desc_init()` plus multicast filtering. Assertions encode the lifecycle split: before registration drivers initialize without userspace concurrency; after registration the devlink lock serializes userspace and driver access.

## State and Persistence Behavior

The header itself stores no state, but it defines the persistent fields that every devlink instance carries. Dump state persists across multipart netlink dump callbacks through `netlink_callback::ctx`, tracking instance index, subobject index, region offsets, health dump timestamps, and resource port context.

## Dependencies and Integration Points

It includes device, netdevice, net namespace, rtnetlink, RDMA verbs, public devlink API, and generated netlink definitions. All devlink C files in this subset depend on it for shared declarations and invariants.

## Risks

Changing `struct devlink` layout or lock semantics affects every devlink module. Dump-state union reuse requires each dump handler to reset fields correctly when moving between instances. Inline notification filters rely on object descriptors containing enough stable identity to filter multicast messages safely.

## Test Signals

Build coverage is the primary signal for prototype drift. Runtime tests should exercise all dump handlers across multiple devlinks and ports, lockdep assertions for registered versus unregistered phases, and multicast filtering by bus, device, index, and port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/devl_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/dpipe.c -->
# sources/distributed-fs/ceph-client/net/devlink/dpipe.c

## Purpose

`dpipe.c` implements devlink's data-path pipeline introspection support. It lets drivers register hardware pipeline headers and tables, expose table matches/actions/entries over netlink, control table counters, and associate tables with devlink resources.

## Important APIs, Types, and Functions

The file exports global header descriptors `devlink_dpipe_header_ethernet`, `devlink_dpipe_header_ipv4`, and `devlink_dpipe_header_ipv6`. Exported helpers include `devlink_dpipe_match_put()`, `devlink_dpipe_action_put()`, `devlink_dpipe_entry_ctx_prepare()`, `devlink_dpipe_entry_ctx_append()`, `devlink_dpipe_entry_ctx_close()`, `devlink_dpipe_entry_clear()`, `devl_dpipe_headers_register()`, `devl_dpipe_headers_unregister()`, `devlink_dpipe_table_counter_enabled()`, `devl_dpipe_table_register()`, `devl_dpipe_table_unregister()`, and `devl_dpipe_table_resource_set()`. Netlink handlers include table get, entries get, headers get, and table counters set.

## Control Flow

Drivers register headers and tables under the devlink lock. Table GET walks the table list, asks each table op for size, matches, and actions, and sends multipart replies when the skb fills. Entries GET finds a named table and delegates entry generation to driver `entries_dump()`, using a dump context that drivers prepare, append entries into, and close. Header GET serializes registered header fields. Counter SET finds a table, rejects externally controlled counters, toggles `counters_enabled`, and calls `counters_set_update()` if supplied.

## State and Persistence Behavior

Persistent state is stored on `struct devlink`: `dpipe_headers` and the RCU-protected `dpipe_table_list`. Each `struct devlink_dpipe_table` stores name, ops, private driver pointer, counter state, optional resource ID/units, and whether counters are externally controlled. Entry values allocated by drivers are cleaned by `devlink_dpipe_entry_clear()`.

## Dependencies and Integration Points

The implementation uses generic netlink attribute construction, devlink handles from `devl_internal.h`, RCU list traversal, and driver-supplied `devlink_dpipe_table_ops`. Resource linkage lets devlink resource accounting describe table capacity.

## Risks

Multipart reply code must handle `-EMSGSIZE` without duplicating or skipping tables/headers. Table lookup mixes lockdep-protected and RCU traversal, so unregister requires RCU free. Driver `entries_dump()` must use the context protocol correctly or replies can be malformed. Counter toggles affect future driver table entries and must not race with hardware updates outside the devlink lock.

## Test Signals

Test header and table registration/unregistration, duplicate table names, table and entry dumps with small skb forcing multipart output, counter enable/disable with and without external control, resource association, entry clear freeing values and masks, and drivers with absent optional ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/dpipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/health.c -->
# sources/distributed-fs/ceph-client/net/devlink/health.c

## Purpose

`health.c` implements devlink health reporters and formatted diagnostic messages. Drivers create reporters for devices or ports, report errors, optionally auto-dump diagnostic state, optionally auto-recover, and expose reporter configuration, dumps, diagnosis, recovery, and tests over devlink netlink.

## Important APIs, Types, and Functions

Core types are private `struct devlink_health_reporter`, `struct devlink_fmsg`, and `struct devlink_fmsg_item`. Reporter APIs include `devl_health_reporter_create()`, `devlink_health_reporter_create()`, port variants, destroy functions, `devlink_health_report()`, `devlink_health_reporter_recovery_done()`, `devlink_health_reporter_state_update()`, and `devlink_health_reporter_priv()`. Formatted message APIs include object/pair/array/binary nest helpers, typed put helpers, pair put helpers, `devlink_fmsg_binary_pair_put()`, and `devlink_fmsg_dump_skb()`. Netlink handlers cover reporter get/set, recover, diagnose, dump get, dump clear, and test.

## Control Flow

Reporter creation validates ops defaults, initializes graceful/burst periods, auto-recover, and auto-dump based on available callbacks, and links the reporter into either the device or port list. `devlink_health_report()` logs a trace event, increments error count, marks error state, sends notification, enforces burst/graceful recovery suppression, optionally stores a dump under devlink lock, and optionally invokes recovery. Dump capture allocates an fmsg, opens an object nest, calls driver `dump()`, closes the nest, stores jiffies and real timestamps, and keeps the dump until cleared or replaced. Diagnosis uses a temporary fmsg and streams it immediately. Dump get caches the dump timestamp in dump state to detect concurrent dump replacement.

## State and Persistence Behavior

Each reporter persists counters, health state, auto settings, periods, last recovery timestamp, dump timestamps, and one cached `dump_fmsg`. Fmsg state is an ordered list of typed items plus a sticky first-error field and binary-mode guard. Recovery burst behavior uses jiffies and recovery counts to avoid repeated automatic recovery after recent errors.

## Dependencies and Integration Points

The file integrates with devlink netlink, devlink ports, tracepoints, skb inspection, and driver-provided `devlink_health_reporter_ops` callbacks for recover, dump, diagnose, and test. It uses devlink locking when storing dumps and invoking recovery from automatic paths.

## Risks

Reporter lifetimes depend on drivers destroying reporters before devlink teardown. Auto-recovery suppression is subtle: previous error state, burst period, graceful period, and last recovery timestamp all influence behavior. Fmsg nesting is protocol-sensitive; binary data must be wrapped with the binary pair API, and oversize items set sticky errors. Multipart dump streaming must detect replacement to avoid mixing old and new dumps. Some notification paths assert registration and can warn if called at the wrong lifecycle point.

## Test Signals

Test reporter create/destroy for device and port reporters, duplicate names, get/set auto flags and periods, error report with auto-dump and auto-recover on/off, recovery abort during bursts, manual recover, diagnose output, dump get/clear with multipart output, concurrent dump replacement returning `-EAGAIN`, fmsg binary misuse returning errors, and `devlink_fmsg_dump_skb()` field emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/health.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/linecard.c -->
# sources/distributed-fs/ceph-client/net/devlink/linecard.c

## Purpose

`linecard.c` implements devlink linecard objects, including creation, user-visible state reporting, provisioning and unprovisioning, active/inactive transitions, supported type discovery, notifications, and optional nested devlink attachment.

## Important APIs, Types, and Functions

The private `struct devlink_linecard` stores devlink pointer, index, ops, private pointer, state, state lock, current type, supported types, and nested relationship index. Exported APIs include `devlink_linecard_index()`, `devl_linecard_create()`, `devl_linecard_destroy()`, `devlink_linecard_provision_set()`, `devlink_linecard_provision_clear()`, `devlink_linecard_provision_fail()`, `devlink_linecard_activate()`, `devlink_linecard_deactivate()`, and `devlink_linecard_nested_dl_set()`. Netlink handlers are `devlink_nl_linecard_get_doit()`, dumpit, and set.

## Control Flow

Drivers create linecards under the devlink lock, providing ops for provision, unprovision, type count, and type get. Creation snapshots supported types and links the linecard. GET serializes index, state, current type, supported types, and nested devlink handle. SET with a non-empty type validates the linecard is not transitioning, checks type support, moves to PROVISIONING, notifies, drops the state lock while calling driver `provision()`, and rolls back to UNPROVISIONED on synchronous failure. SET with an empty type moves through UNPROVISIONING and calls driver `unprovision()`, with special handling for PROVISIONING_FAILED and already-unprovisioned states. Drivers later call provision/activation helpers for asynchronous completion.

## State and Persistence Behavior

Linecard state persists in `devlink->linecard_list`. `state_lock` protects `state` and `type`; the broader devlink lock protects list membership. Supported type strings and private type pointers are captured at creation. Nested devlink relationships persist by relationship index and are cleaned when the nested object disappears.

## Dependencies and Integration Points

The file uses devlink generic netlink, notification helpers, and relationship support from `core.c`. Driver callbacks implement hardware-specific provisioning. Register/unregister fanout in `dev.c` emits linecard notifications for existing objects.

## Risks

State transitions are asynchronous-friendly but require drivers to call completion helpers consistently. `devlink_linecard_nested_dl_set()` always adds a relationship and does not directly handle `NULL` despite the comment mentioning detach, so caller expectations should be checked against current implementation. Failure paths assume unprovisioned future state. Notifications require registered devlink state and can be missed if listeners attach after transitions.

## Test Signals

Test duplicate linecard indexes, unsupported types, same-provision success, provision/unprovision busy states, synchronous provision failure rollback, asynchronous provision set/fail/clear, activate/deactivate warnings, dump continuation across multiple linecards, and nested devlink handle notification/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/linecard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/netlink.c -->
# sources/distributed-fs/ceph-client/net/devlink/netlink.c

## Purpose

`netlink.c` provides the generic netlink family glue for devlink. It implements multicast groups, per-socket notification filters, devlink handle lookup from attributes, pre/post operation locking, common dump iteration, nested handle emission, and the `devlink_nl_family` registration descriptor.

## Important APIs, Types, and Functions

Important functions are `devlink_nl_notify_filter_set_doit()`, `devlink_nl_notify_filter()`, `devlink_nl_put_nested_handle()`, `devlink_nl_msg_reply_and_new()`, `devlink_get_from_attrs_lock()`, pre-doit variants for devlink, port, device-lock, and optional-port operations, post-doit variants, and `devlink_nl_dumpit()`. The per-socket state is `struct devlink_nl_sock_priv`, holding an RCU-protected `struct devlink_obj_desc` filter.

## Control Flow

Users may install a notification filter by bus name, device name, devlink index, and/or port index. Multicast sends call `devlink_nl_notify_filter()`, which reads the socket filter under RCU and suppresses nonmatching messages. Operation pre-doit resolves a devlink by index or bus/device pair, takes a reference, locks the instance and optionally the parent device, validates registration, and optionally resolves a port into `info->user_ptr[1]`. Post-doit unlocks and drops the reference. Dumps either target a single requested instance or iterate all registered instances in the caller's net namespace, resetting subobject dump state between devlinks.

## State and Persistence Behavior

Notification filter state persists per generic-netlink socket until replaced or socket destruction, then is freed by RCU. Dump progress persists in `struct devlink_nl_dump_state` inside the netlink callback context. Devlink references acquired during pre-doit and dump iteration are released after each operation.

## Dependencies and Integration Points

The file depends on generated `devlink_nl_ops`, `devlink_nl_family`, xarray lookup from `core.c`, port lookup helpers, generic netlink socket-private support, namespace ID allocation for nested handles, and multicast filtering hooks.

## Risks

Lookup supports either index or bus/device identity; accepting mixed identifiers would be ambiguous and is rejected. Pre/post flag mismatches can leave device locks held or drop references incorrectly. Filter string storage uses one allocation with embedded string data, so offset calculations must remain correct. Dump handlers must correctly use and reset shared dump-state fields.

## Test Signals

Test lookup by index, synthetic index bus name, and real bus/device; operations against unregistering devlinks; required and optional port pre-doit paths; device-lock paths under lockdep; notification filters for each field; nested handle netns ID emission; and multi-instance dumps with skb-size induced continuation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/netlink.c -->
