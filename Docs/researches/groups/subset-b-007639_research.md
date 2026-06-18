# subset-b-007639 Research

Grouped research for the requested Lustre LNet UAPI, LNet build/include, and EFA/GNI LND files. Each section is source-tree-aligned and can be split into its mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-types.h -->
# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-types.h

## Purpose
This UAPI header defines core LNet public types and constants shared by kernel code, user utilities, and wire-facing structures. It covers legacy 64-bit NID helpers, large `struct lnet_nid` helpers, LNet process IDs, memory descriptor configuration, event queue records, counters, and UDSP action identifiers.

## Important APIs, Types, And Functions
Key NID helpers include `LNET_NIDADDR()`, `LNET_NIDNET()`, `LNET_NETNUM()`, `LNET_NETTYP()`, `LNET_MKNET()`, `LNET_MKNID()`, `lnet_nid4_to_nid()`, `lnet_nid_to_nid4()`, `nid_same()`, `nidhash()`, `LNET_NID_NET()`, `nid_is_nid4()`, and `nid_addr_is_set()`. `struct lnet_handle_md` plus `LNetInvalidateMDHandle()` and `LNetMDHandleIsInvalid()` define the public memory descriptor handle contract. `struct lnet_process_id` is the old NID4 process ID, while `struct lnet_processid` carries large NIDs; `lnet_pid4_to_pid()` and `lnet_pid_to_pid4()` bridge them. `struct lnet_md`, `enum lnet_md_options`, `enum lnet_event_kind`, `struct lnet_event`, `struct lnet_counters`, and `enum lnet_ack_req` are the main user-visible LNet API payloads.

## Control Flow
The file is almost entirely inline conversion and predicate logic. NID4 conversion maps the 32-bit network and 32-bit address into `struct lnet_nid` fields using big-endian storage for `nid_num` and `nid_addr[0]`; converting back reconstructs a legacy `lnet_nid_t`. MD and event structures are passive ABI payloads consumed by LNet API calls and event handlers. `nid_addr_is_set()` scans the address byte span reported by `NID_ADDR_BYTES()` to distinguish network-only from full NID input, with an explicit ambiguity for address zero.

## State, Persistence, And Dependencies
There is no runtime state or persistence. The header depends on fixed UAPI layout from `lnet-idl.h`, Linux integer types, byte-order helpers, and `PAGE_SHIFT`. Because many structures cross the user/kernel or wire boundary, field order, sizes, endian handling, and reserved values are persistent ABI.

## Integration Points
It is included by LNet UAPI headers, LNet kernel internals, utilities that parse NIDs, LND implementations, and selftest/fault-injection ioctls. EFA LND uses the large-NID helpers and the old/new NID conversion paths for protocol compatibility.

## Risks
The main risk is ABI drift: changing enum values, structure layout, or NID encoding breaks user tools and peer compatibility. `nid_addr_is_set()` can misclassify valid zero-address NIDs as unset, so callers must not use it as a proof that a user omitted the address. NID4 conversion loses large-NID address bytes. Event handlers are documented as nonblocking and unable to call LNet APIs; violations can deadlock or corrupt event sequencing.

## Test Signals
Useful tests exercise NID4 to large-NID round trips, any-NID handling, zero-address NID parsing, MD option validation, event field population for PUT/GET/ACK/REPLY/SEND/UNLINK, and ABI size checks for UAPI structs compiled in kernel and userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnetctl.h -->
# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnetctl.h

## Purpose
This UAPI header defines `/dev/lnet` fault-simulation ioctl payloads for LNet message drop and delay rules. It also exposes the device ID and path used by user tools.

## Important APIs, Types, And Functions
The command enum identifies add/delete/reset/list operations for drop and delay simulation. Message-type bits cover ACK, PUT, GET, and REPLY. Health-status bits encode local interrupt, local drop, local abort, no-route, local error, local timeout, remote error/drop/timeout, network timeout, and random health selection. `struct lnet_fault_attr` describes rule match fields and either drop or delay attributes. `struct lnet_fault_stat` reports matched, per-message-type, dropped, and delayed counts.

## Control Flow
User space fills `lnet_fault_attr` and sends it through the LNet control path. Source, destination, local NID, portal mask, and message mask gate whether a message is eligible. The union then selects drop behavior by rate or interval and health error mask, or delay behavior by rate or interval plus latency. Kernel fault-injection code updates `lnet_fault_stat` counters as matching messages are processed.

## State, Persistence, And Dependencies
The header itself stores no state. The kernel keeps rule state and counters after ioctls are applied. It depends on `lnet-types.h` for `lnet_nid_t` and on Linux fixed-width integer types. The union includes spare space to preserve ABI room.

## Integration Points
LNet test tools and administrative utilities include this file to configure message loss/latency fault injection through `LNET_DEV_PATH`. The masks line up with LNet message kinds and health counters exposed elsewhere in LNet.

## Risks
Because this is UAPI, command values and struct layout are compatibility-sensitive. Portal masks are 64-bit, so callers must ensure portal indexes fit the mask. Rate and interval fields are mutually exclusive by comment but require kernel validation. A broad wildcard rule can disrupt live traffic if accidentally installed.

## Test Signals
Tests should add, list, reset, and delete drop and delay rules; verify wildcard and portal/message masks; check that mutually exclusive rate/interval inputs are rejected or handled predictably; and confirm health counters reflect injected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnetctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnetst.h -->
# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnetst.h

## Purpose
This UAPI header defines the ioctl and generic-netlink-facing ABI for LNet selftest. It describes sessions, groups, batches, tests, debug/stat requests, test parameters, and wire counters used by the selftest framework.

## Important APIs, Types, And Functions
Important constants include `LST_FEAT_BULK_LEN`, `LST_NAME_SIZE`, the `LSTIO_*` ioctl command values, node state bits, batch/group operation codes, `LST_DEFAULT_BATCH`, `LST_MAX_CONCUR`, and the `LNET_SELFTEST_*` generic netlink identifiers. `struct lst_sid` and `struct lst_bid` identify sessions and batches. The `lstio_*_args` structs are the user/kernel ioctl payloads for session, group, node, batch, test, debug, and stats operations. `struct lstcon_trans_stat` stores RPC/framework counters; inline helpers increment or read fixed slots in those arrays. `struct lst_test_bulk_param`, `struct lst_test_ping_param`, `struct srpc_counters`, and `struct sfw_counters` define test parameters and returned counters.

## Control Flow
Users create a session, add groups and nodes, add batches and tests, start or stop batches, query status, and request stats/debug data through ioctl payloads. Many payloads carry `__user` pointers to variable-length buffers or result list heads. Transaction helpers update different indexes in `trs_rpc_stat` and `trs_fwk_stat` depending on the operation family, so consumers must interpret the same arrays according to context. Bulk and ping test parameters select operation type, size, timing, loop count, validation flags, and concurrency.

## State, Persistence, And Dependencies
The header stores no live state, but its structures are the persistent ABI between selftest user tools and kernel modules. It depends on `lnet-types.h` for process IDs and on Linux time/types. `srpc_counters` and `sfw_counters` are packed because they are sent over the wire.

## Integration Points
Selftest controller code, user utilities, and generic netlink handlers consume these definitions. The test framework also depends on LNet process IDs, list-head compatibility stubs for user builds, and LNet message transport underneath the test RPCs.

## Risks
The ABI uses raw `__user` pointers and list heads, so copy-in/copy-out length validation is critical. Inline statistic helpers assume fixed array indexes; off-by-one or context confusion can report wrong states. Some comments contain legacy spellings and stale wording, which raises documentation risk but not direct runtime risk. Packed wire counters must remain layout-stable.

## Test Signals
Exercise full session lifecycle, group add/update/list/info, batch add/start/query/stop/delete, bulk and ping test creation, debug result lists, and stats queries. ABI tests should verify struct sizes, command values, packed counter layout, feature negotiation, maximum concurrency handling, and invalid pointer/length rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnetst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/nidstr.h -->
# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/nidstr.h

## Purpose
This UAPI header assigns stable numeric IDs to Lustre Network Drivers and declares the shared NID/network string parsing, formatting, range parsing, and matching APIs used by kernel code and user utilities.

## Important APIs, Types, And Functions
The LND enum assigns values for active drivers such as `SOCKLND`, `O2IBLND`, `LOLND`, `GNILND`, `GNIIPLND`, `PTL4LND`, `KFILND`, `TOFULND`, `EFALND`, and `BXI3LND`, while retaining commented historical values. Formatting helpers include `libcfs_lnd2str_r()`, `libcfs_net2str_r()`, `libcfs_nid2str_r()`, and `libcfs_nidstr_r()` plus inline ring-buffer wrappers. Parsing and matching APIs include `libcfs_str2lnd()`, `libcfs_str2net()`, `libcfs_str2nid()`, `libcfs_strnid()`, `libcfs_str2anynid()`, `libcfs_stranynid()`, `cfs_parse_nidlist()`, `cfs_match_nid()`, `cfs_match_net()`, `cfs_ip_addr_parse()`, and `libcfs_ip_in_netmask()`.

## Control Flow
Formatting callers can either provide explicit buffers or use `libcfs_next_nidstring()` through inline helpers that return one of the shared fixed-size string slots. Parsing functions translate strings into LND IDs, network IDs, legacy NIDs, large NIDs, numeric ranges, and IP/netmask expressions. Matching functions compare a concrete NID, network, or IP address against parsed lists.

## State, Persistence, And Dependencies
The numeric LND values are persistent protocol/address ABI and must not be renumbered. The header declares a shared rotating string buffer contract through `LNET_NIDSTR_COUNT` and `LNET_NIDSTR_SIZE`, but the storage lives in implementation files. It depends on `lnet-types.h` and a forward-declared `struct list_head`.

## Integration Points
All LNet configuration paths, diagnostics, logs, NID parsers, LNDs, and user tools use these declarations. EFA LND depends on `EFALND`, `SOCKLND`, and string helpers for NID generation, TCP metadata discovery, logging, and module registration.

## Risks
Changing LND enum values breaks persisted NIDs and routing compatibility. The inline formatting wrappers return shared buffer slots, so callers must not assume indefinite lifetime or thread ownership beyond the implementation contract. Parser APIs mutate some input strings and consume `list_head` outputs, making ownership and cleanup with `cfs_free_nidlist()` or `cfs_expr_list_free_list()` important.

## Test Signals
Tests should cover every active LND string round trip, historical/reserved numeric stability, IPv4 and large-NID formatting, wildcard NID parsing, NID range min/max discovery, netmask matching, delimiter discovery, and cleanup of parsed expression lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/nidstr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/socklnd.h -->
# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/socklnd.h

## Purpose
This small UAPI header defines shared socket LND connection type constants used by the socknal implementation and utilities.

## Important APIs, Types, And Functions
Constants are `SOCKLND_CONN_NONE`, `SOCKLND_CONN_ANY`, `SOCKLND_CONN_CONTROL`, `SOCKLND_CONN_BULK_IN`, `SOCKLND_CONN_BULK_OUT`, `SOCKLND_CONN_NTYPES`, and alias `SOCKLND_CONN_ACK`.

## Control Flow
There is no executable control flow. Consumers use these values to classify socket connections by control traffic, inbound bulk, outbound bulk, or wildcard/none selection.

## State, Persistence, And Dependencies
No state is stored. The constants are ABI shared between kernel and tools, so their numeric values are persistent.

## Integration Points
The header is included by socklnd internals and administrative/user utilities that display or configure socklnd connection classes.

## Risks
Renumbering values breaks tool/kernel interpretation. The alias `SOCKLND_CONN_ACK` maps to bulk-in, so code that treats ACK as a separate connection type would be wrong.

## Test Signals
Test signals are compile coverage in socklnd and utilities, connection-class display/configuration round trips, and assertions that `SOCKLND_CONN_NTYPES` stays aligned with implemented connection arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/socklnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/Makefile -->
# sources/distributed-fs/lustre-release/lnet/Makefile

## Purpose
This Kbuild makefile declares the top-level LNet module subdirectories to build: core LNet, kernel LNDs, and selftest.

## Important APIs, Types, And Functions
The only build rules are `obj-m += lnet/`, `obj-m += klnds/`, and `obj-m += selftest/`.

## Control Flow
During an out-of-tree Lustre kernel-module build, Kbuild descends into each listed subdirectory and evaluates its own makefile. This file does not apply config gating itself; the subdirectories contain their own object selection.

## State, Persistence, And Dependencies
No runtime state exists. The persistent behavior is build graph inclusion: omitting a directory here prevents its child makefiles from contributing modules.

## Integration Points
It connects the Lustre build system to core LNet code, LND modules, and the selftest module tree.

## Risks
Accidental removal or reordering can omit modules from builds or affect build diagnostics. Because all entries are `obj-m`, downstream config gates must be correct in child makefiles.

## Test Signals
Build tests should verify that `lnet/`, `klnds/`, and `selftest/` are entered and that expected modules appear under representative configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/include/lock.h -->
# sources/distributed-fs/lustre-release/lnet/include/lock.h

## Purpose
This internal LNet header declares a CPU-partition lock abstraction for data that is usually updated per CPU partition but occasionally needs global exclusion.

## Important APIs, Types, And Functions
`CFS_PERCPT_LOCK_EX` requests exclusive locking across all private locks. `struct cfs_percpt_lock` stores the CPT table, exclusive state, and per-partition spinlock table. Public APIs are `cfs_percpt_lock_create()`, `cfs_percpt_lock_free()`, `cfs_percpt_lock()`, and `cfs_percpt_unlock()`. `cfs_percpt_lock_num()` reports the number of private locks. `cfs_percpt_lock_alloc()` wraps creation with a static `lock_class_key` array for lockdep.

## Control Flow
Callers create a lock for a `cfs_cpt_table`, lock either a single partition index or the exclusive sentinel, update protected data, then unlock the same scope. The allocation macro uses static lockdep keys when the CPT count fits `CFS_PERCPT_LOCK_KEYS`, otherwise it falls back to no explicit key array.

## State, Persistence, And Dependencies
The lock object owns spinlock storage and records whether it is exclusively locked. There is no persistence beyond kernel memory. It depends on libcfs CPT APIs, spinlocks, and lockdep key types.

## Integration Points
LNet code uses this pattern for per-CPT structures with rare global mutation, matching the topology used by schedulers, network data, and routing/peer tables.

## Risks
Deadlock risk exists if callers mix partition and exclusive locking in inconsistent order or unlock with a different index. Lockdep class coverage is limited to 256 CPTs by the macro. The header exposes only declarations, so implementation correctness is in the corresponding C file.

## Test Signals
Concurrency tests should cover per-partition parallel access, exclusive exclusion against all partitions, lock/unlock balance, CPT counts above and below 256, and lockdep warnings under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/include/lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/include/udsp.h -->
# sources/distributed-fs/lustre-release/lnet/include/udsp.h

## Purpose
This internal header declares User Defined Selection Policy management APIs for LNet. UDSP policies influence route, peer, network, and NI selection by applying priorities or preferred lists to matching constructs.

## Important APIs, Types, And Functions
Policy list management uses `lnet_udsp_add_policy()`, `lnet_udsp_get_policy()`, and `lnet_udsp_del_policy()`. Application hooks are `lnet_udsp_apply_policies()`, `lnet_udsp_apply_policies_on_lpni()`, `lnet_udsp_apply_policies_on_lpn()`, `lnet_udsp_apply_policies_on_ni()`, and `lnet_udsp_apply_policies_on_net()`. Lifecycle helpers are `lnet_udsp_alloc()`, `lnet_udsp_free()`, and `lnet_udsp_destroy()`. User/kernel conversion is represented by `lnet_get_udsp_size()`, `lnet_udsp_marshal()`, `lnet_udsp_demarshal_add()`, and `lnet_udsp_get_construct_info()`.

## Control Flow
Management functions require the LNet API mutex. Applying all policies may target all stored policies or a single passed policy and can also revert effects. Object-specific application functions require both the API mutex and exclusive LNet network lock. Marshal/demarshal paths convert between internal `struct lnet_udsp` and ioctl bulk payloads.

## State, Persistence, And Dependencies
The header declares APIs over a global policy set owned by LNet implementation files. Policy state persists in kernel memory until deletion or `lnet_udsp_destroy()`. It depends on `lib-lnet.h`, LNet peer/net/NI structures, and ioctl UDSP payload definitions.

## Integration Points
LNet configuration ioctls and netlink/control paths create policies; route/peer/NI management invokes the apply helpers when constructs are added, removed, refreshed, or queried.

## Risks
The locking preconditions are critical. Calling apply helpers while holding `lnet_net_lock` where forbidden, or without `LNET_LOCK_EX` where required, can deadlock or race policy state. Marshal size mismatches can corrupt user/kernel exchange. Revert behavior must mirror apply behavior exactly.

## Test Signals
Tests should add/delete/reorder policies, apply to existing and newly added peers/NIs/nets, revert policies, marshal/demarshal round trip complex descriptors, query construct info, and run lockdep-enabled policy churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/include/udsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/Makefile -->
# sources/distributed-fs/lustre-release/lnet/klnds/Makefile

## Purpose
This Kbuild makefile selects which kernel LNet Network Driver subdirectories participate in the build.

## Important APIs, Types, And Functions
Config-gated entries are `CONFIG_LNET_GNILND`, `CONFIG_LNET_O2IBLND`, `BUILD_EXT_O2IB`, `CONFIG_LNET_KFILND`, and `CONFIG_LNET_EFALND`. `socklnd/` is always included as an external module entry.

## Control Flow
Kbuild evaluates config symbols and optional `BUILD_EXT_O2IB` to decide which child directories to visit. In-kernel O2IB and external O2IB are mutually represented by separate entries.

## State, Persistence, And Dependencies
No runtime state exists. Build output depends on kernel config, Lustre build variables, and child makefiles.

## Integration Points
This file connects the top-level LNet build to GNILND, O2IBLND, KFILND, EFALND, and SOCKLND module builds.

## Risks
Incorrect config symbols can silently omit an LND. Always building `socklnd/` means its child makefile must handle unsupported configurations correctly. External O2IB selection depends on the build environment variable being set consistently.

## Test Signals
Matrix builds should verify each LND config independently, all enabled together, external O2IB mode, and absence of unexpected modules when configs are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/Makefile -->
# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/Makefile

## Purpose
This Kbuild makefile builds the EFA LNet Network Driver module `kefalnd.o` from its implementation files and exposes the EFA provider include path.

## Important APIs, Types, And Functions
`kefalnd-objs` includes `efalnd.o`, `efalnd_modparams.o`, `efalnd_peerni.o`, `efalnd_connection.o`, and `efalnd_debugfs.o`. `NOSTDINC_FLAGS += -I $(EFA_INCLUDE_PATH)` adds the EFA kernel verbs headers. `CONFIG_GCOV_PROFILE_LNET` enables `GCOV_PROFILE`.

## Control Flow
When the parent makefile includes `efalnd/`, Kbuild links the listed objects into `kefalnd.o`. The include path must resolve `efa_verbs.h` and related EFA-specific definitions during compilation.

## State, Persistence, And Dependencies
No runtime state exists. The build depends on `EFA_INCLUDE_PATH`, RDMA/EFA kernel headers, and the Lustre/LNet include tree.

## Integration Points
It is selected by `CONFIG_LNET_EFALND` in `lnet/klnds/Makefile` and produces the module that registers the `EFALND` LNet driver at init.

## Risks
Missing or incompatible `EFA_INCLUDE_PATH` breaks compilation. Omitting one object file can remove module parameters, peer metadata discovery, connection state handling, or debugfs support. GCOV profile support should remain conditional to avoid unwanted instrumentation.

## Test Signals
Build tests should compile EFALND with and without GCOV, validate that all object files link into `kefalnd.o`, and verify include path failures are caught early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd.c

## Purpose
This is the main implementation of Amazon EFA LND for LNet. It registers the `EFALND` transport, manages EFA RDMA resources, maps LNet messages to EFA immediate or RDMA-read protocol flows, polls completions, starts per-CPT scheduler and connection-manager threads, and handles NI/device startup and shutdown.

## Important APIs, Types, And Functions
External LND entry points are wired through `the_efalnd`: `kefalnd_startup()`, `kefalnd_shutdown()`, `kefalnd_send()`, `kefalnd_recv()`, `kefalnd_get_dev_prio()`, and `kefalnd_get_nid_metadata()`. Protocol helpers include `kefalnd_msgtype2size()`, `kefalnd_efa_status_to_errno()`, `kefalnd_errno_to_efa_status()`, `kefalnd_init_tx_protocol_msg()`, `kefalnd_get_srcnid_from_msg()`, and `kefalnd_get_dstnid_from_msg()`. Resource helpers manage TX/FMR pools, QPs, CQs, RX buffers, DMA mapping, and FMR registration/invalidation. Runtime handlers include `kefalnd_send()`, `kefalnd_recv()`, `kefalnd_handle_rx()`, `kefalnd_tx_complete()`, `kefalnd_rx_complete()`, `kefalnd_scheduler()`, `kefalnd_dev_init()`, `kefalnd_create_efa_nid()`, `kefalnd_base_startup()`, and `kefalnd_base_shutdown()`.

## Control Flow
Module init initializes tunables/debugfs and registers the LND. NI startup creates global state if needed, allocates `struct kefa_ni`, selects an IPv4 underlay interface, opens an EFA RDMA device by name, allocates PD/CQ/QP/FMR resources, creates either a small or large EFA NID, creates TX pools, starts scheduler and connection-manager threads, and links the NI into global lists. Sending obtains a TX, finds or starts an initiator connection, and chooses immediate send for small non-GPU payloads or RDMA-read handshakes for larger/GPU PUT, REPLY, and GET traffic. Receiving validates EFALND headers, dispatches LNet request messages into `lnet_parse()`, handles GETR/PUTR completion messages, and forwards connection-establishment packets to `efalnd_connection.c`. Scheduler threads poll CQs in batches and call completion handlers for send, recv, MR registration, RDMA read, and local invalidate completions.

## State, Persistence, And Dependencies
Global state lives in `struct kefa_data kefalnd`: NI list, per-CPT schedulers, per-CPT connection daemons, peer-NI rhashtable, thread count, shutdown flag, and init state. Per-NI state includes epoch, TX pool, connection hash table, cleanup list, and EFA device pointer. Per-device state includes RDMA device, GID, PD, QPs, CQs, FMR pool, local QP selection, interface IP, and CPT. Per-TX state tracks mapped fragments, FMR, RDMA descriptor, completion refs, waiting response flag, send time, and LNet messages to finalize. State is in kernel memory only and is torn down on NI/module shutdown.

## Integration Points
This file depends on LNet core (`lnet_parse()`, `lnet_finalize()`, NI tunables, NID helpers, RDMA utility mapping), Linux RDMA verbs, EFA-specific SRD QP support, libcfs CPT allocation/binding, debug/logging helpers, and connection/peer helpers in the companion EFALND files. Large-NID support integrates with `lnet-types.h`; small-NID support integrates with TCP metadata discovery.

## Risks
Resource cleanup is complex: DMA maps, FMR state, pending FINVs, QPs, CQs, TX refs, and LNet finalization must balance across success, error, timeout, and shutdown. Several TODOs note missing fatal CQ error handling and potential stuck pending TXs after `ib_post_send()` returns `-ENOMEM`. Header validation rejects epoch mismatches and unsupported v1 traffic except connection probes; version negotiation must stay compatible. FMR allocation failure after DMA mapping needs careful unmap via the error path. Small-NID construction assumes IPv4 underlay and PCI parent availability.

## Test Signals
Strong signals include module build/load/unload, NI startup/shutdown with real or mocked EFA devices, immediate PUT/GET/REPLY/ACK traffic, RDMA PUTR and GETR flows, GPU MD forcing RDMA, protocol version and epoch mismatch rejection, CQ completion stress, RNR retry behavior, FMR registration/invalidation churn, low-memory TX/FMR pool failures, connection timeout cleanup, and LNet finalization status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd.h

## Purpose
This private EFALND header defines module constants, core runtime structures, state enums, inline helpers, and cross-file function prototypes for the EFA LNet driver.

## Important APIs, Types, And Functions
Important constants include EFALND version numbers, MTU/message sizes, TX pool and fragment limits, scheduler thread defaults, static small-NID CM QKEY, RDMA threshold, connection hash bits, invalid connection marker, maximum peer QPs, and large-NID field offsets. Main structures are `kefa_data`, `kefa_tunables`, `kefa_peer_ni`, `kefa_obj_pool`, `kefa_rx`, `kefa_qp`, `kefa_cq`, `kefa_fmr`, `kefa_dev`, `kefa_tx`, `kefa_ni`, `kefa_conn`, `kefa_cm_deamon`, and `kefa_sched`. Enums describe init state, FMR state, connection state, and connection type. Inline helpers build/extract large NIDs, compute LND version, stop threads, and set message epoch.

## Control Flow
The header is the shared contract between main transport, connection handling, peer metadata, modparams, and debugfs. Runtime flow is represented by state fields: FMRs move inactive/activating/active/deactivating, connections move inactive through TCP/EFA probe, establishment, active, and deactivating, and TXs carry refs and optional sync-completion state.

## State, Persistence, And Dependencies
All structures are in-memory kernel state. The large-NID layout is an inter-node protocol/address contract: bytes 0-1 store CM QP number, 2-3 store QKEY, and 4-15 store the nonconstant EFA GID suffix. The header depends on libcfs, LNet library internals, LNet RDMA helpers, Linux rhashtable/list/spin/kref APIs, and `efa_verbs.h`.

## Integration Points
Every EFALND C file includes this header. It also bridges to LNet `struct lnet_ni`, `struct lnet_msg`, `struct lnet_nid`, ioctl EFALND tunables, and protocol structures from `efalnd_proto.h`.

## Risks
Structure fields are highly coupled to completion handlers and cleanup code; changing list ownership, ref counters, or state enums can introduce races. The large-NID helper assumes the first four GID bytes are constant and reconstructs them as `fe80::`, which must match EFA behavior. `peer_ni_params` keys only `remote_nid_addr`, so small-NID uniqueness depends on the generated address scheme.

## Test Signals
Tests should compile all EFALND files against this header, validate large-NID create/extract round trips, exercise connection and FMR state transitions, run lock/refcount checking on peer-NI and TX lifetimes, and verify version/protocol constants match wire compatibility expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_connection.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_connection.c

## Purpose
This file implements EFALND connection establishment, lookup, refresh, deactivation, timeout scanning, and connection-manager daemon behavior.

## Important APIs, Types, And Functions
Public functions are `kefalnd_lookup_or_init_conn()`, `kefalnd_lookup_conn()`, `kefalnd_handle_conn_establishment()`, `kefalnd_deactivate_conn()`, `kefalnd_destroy_conn()`, `kefalnd_cm_daemon()`, `kefalnd_add_ni_to_cm_daemon()`, and `kefalnd_del_ni_from_cm_daemon()`. Internal helpers send connection probe/probe response/request/request ack messages, select data QPs, create AHs, create connections, initialize peer data QPs, refresh responder connections after epoch changes, and clean up timed-out TXs.

## Control Flow
Initiator lookup first searches the per-NI connection hash; on miss it creates a connection and calls `kefalnd_establish_conn()`. Small NIDs perform TCP metadata discovery through `kefalnd_find_remote_peer_ni()` before creating an address handle; large NIDs extract GID and CM QP data directly. Non-loopback initiators send an EFA probe, process probe response/version negotiation, send a connection request with data QPs, and become active after request ack. Responders are created on incoming probes, validate protocol support, record peer epoch/caps, send probe response, process connection request data QPs, become active, and send request ack. Active connection TX queues are posted when the state changes to active.

## State, Persistence, And Dependencies
Connections are stored in `efa_ni->conns` under `conn_lock`, keyed by XOR-derived NID hash. Each connection owns state, AH, peer QP array, remote epoch/caps, pending/active/abort TX lists, type, and optional peer-NI reference. Cleanup candidates are moved to `efa_ni->cleanup_conns`; the CM daemon scans every second and performs idle scans every fifth iteration. There is no persistence beyond kernel memory, but epochs are used to detect peer restart/stale connections.

## Integration Points
The file relies on message layout from `efalnd_proto.h`, TX posting and completion helpers from `efalnd.c`, peer metadata from `efalnd_peerni.c`, LNet timeout/tunable values, RDMA address-handle creation, and large/small NID helpers from `efalnd.h`.

## Risks
Connection state transitions happen under a mix of NI rwlock and per-connection spinlock, so lock ordering is critical. The hash key is not a full equality key; lookup also compares full NID, but deactivating connections are reinserted with hash key zero for daemon cleanup. Protocol downgrade is only handled on `-EPROTONOSUPPORT`; other probe failures destroy the connection. Timeout cleanup manipulates TX refs to avoid deadlock, which is fragile under concurrent completions. `RESP_CONN_EXTRA_TIME` means responder connections live longer than initiators and must be tested for stale cleanup.

## Test Signals
Tests should cover initiator and responder handshakes, loopback connection activation, small-NID TCP metadata discovery, large-NID direct metadata, protocol downgrade/no-overlap failure, epoch refresh replacing responder connections, pending TX posting after activation, idle timeout cleanup, TX timeout abort, concurrent lookup/create races, and module shutdown draining daemon lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_connection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_debugfs.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_debugfs.c

## Purpose
This file exposes EFALND debugfs diagnostics for peer-NI metadata, primarily cached GID/QP mappings used for small-NID EFA connection discovery.

## Important APIs, Types, And Functions
`kefalnd_debugfs_init()` creates the `kefalnd` debugfs directory, `peerni_count`, and read-only `gidmap`. `kefalnd_debugfs_exit()` removes the tree. `gidmap_seq_show()` walks `kefalnd.peer_ni` and prints peer address, GID, CM QP number, and QKEY. `LDEBUGFS_SEQ_FOPS_RO(gidmap)` declares the seq-file operations.

## Control Flow
On module init, debugfs entries are created if debugfs allows it. Reading `gidmap` takes RCU read lock, skips output when EFALND is shutdown or uninitialized, starts an rhashtable walk, formats each non-error peer entry, and releases the iterator and RCU lock. Module exit removes the directory recursively.

## State, Persistence, And Dependencies
No separate state is stored except the root `dentry *`. Output reflects live peer-NI rhashtable state and `peer_ni_count`. Data is transient debug state, not persistent configuration. Dependencies include debugfs, seq_file through Lustre debugfs macros, rhashtable iteration, RCU, and EFALND globals.

## Integration Points
The debug entries are initialized from `efalnd.c` module init and removed from module exit. Peer mappings are populated by `efalnd_peerni.c` and consumed by connection setup.

## Risks
The rhashtable walk runs under RCU and reads peer fields without taking each peer's rwlock, so it is diagnostic best-effort and can observe concurrent updates. `debugfs_create_atomic_t()` is called before global startup initializes peer count for first NI, but the atomic object is global and zeroed at module init. Output address formatting uses `remote_nid_addr` byte shifts and must match small-NID encoding expectations.

## Test Signals
Tests should load/unload with debugfs enabled and disabled, read empty `gidmap`, populate peer mappings through TCP discovery, verify `peerni_count`, and stress reads while peer entries are inserted, updated, and freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_modparams.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_modparams.c

## Purpose
This file defines EFALND module parameters and applies default/tunable values to LNet NI configuration during startup.

## Important APIs, Types, And Functions
Module parameters are `nscheds`, `nqps`, `credits`, `peer_credits`, `peer_buffer_credits`, `peer_timeout`, `rnr_retry_count`, and `ipif_name`. `kefalnd_tunables` exposes pointers to scheduler count, RNR retry count, and IP interface name. `kefalnd_tunables_init()` initializes default EFALND LND tunables. `kefalnd_tunables_setup()` copies defaults when no NI-specific tunables were supplied, stamps the LND version, fills common network tunables, clamps peer credits, enforces minimum connection timeout, and sets default QP count.

## Control Flow
Module parameter values are parsed by the kernel module subsystem before EFALND startup. At NI startup, `kefalnd_tunables_setup()` merges module defaults and NI/network tunables: unset common tunables (`-1`) are replaced, peer credits are clamped to EFALND min/max and max-tx credits, peer timeout is raised to `EFALND_MIN_INIT_CONN_TIMEOUT`, and zero `lnd_nqps` is replaced with the module `nqps`.

## State, Persistence, And Dependencies
Parameter values live in module memory and some are read-only after load (`0444`), while `rnr_retry_count` is writable (`0644`). `default_tunables` persists for future NI setup calls. The file depends on LNet default credit/timeout constants and EFALND version helpers.

## Integration Points
`efalnd.c` calls `kefalnd_tunables_init()` at module init and `kefalnd_tunables_setup()` during NI startup. QP count drives CQ/QP allocation; RNR retry drives QP RTS setup; `ipif_name` drives IPv4 underlay interface selection.

## Risks
Bad defaults can over-allocate QPs/TX pools or under-provision credits. Enforcing a minimum peer timeout may surprise configurations that attempt shorter failure detection. Writable `rnr_retry_count` affects new QPs but not necessarily existing QPs. `ipif_name` must select an IPv4 interface or startup fails.

## Test Signals
Tests should load with default parameters, explicit QP/scheduler/credit settings, invalid low peer credits/timeouts, runtime RNR changes before creating a new NI, missing or IPv6 `ipif_name`, and NI-specific tunables overriding module defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_modparams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_peerni.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_peerni.c

## Purpose
This file implements EFALND peer-NI metadata discovery and caching. For small IPv4-style EFA NIDs, it discovers remote EFA GID and CM QP information by issuing an LNet TCP metadata ping and caches results in a global rhashtable.

## Important APIs, Types, And Functions
Public functions are `kefalnd_lookup_or_create_peer_ni()`, `kefalnd_put_peer_ni()`, `kefalnd_update_peer_ni()`, `kefalnd_find_remote_peer_ni()`, and `kefalnd_get_nid_metadata()`. Internal helpers include `efa_nid_to_tcp_nid()`, `peer_ni_free()`, and `get_peer_ni()`. The metadata payload uses `struct kefa_nid_md_entry` from `efalnd_proto.h`.

## Control Flow
For small NIDs, `kefalnd_find_remote_peer_ni()` first looks up the EFA NID address in the peer rhashtable. On miss, it derives the remote TCP NID by combining the local underlay subnet with the EFA NID host bytes, calls `lnet_discover_nid_metadata()` with a 30 second timeout, scans returned mappings for EFALND entries matching the requested address, and inserts or retrieves a `kefa_peer_ni` with GID, CM QP number, and QKEY. Local nodes publish their own metadata through `kefalnd_get_nid_metadata()`, which fills the ping reply entry from the local EFA device.

## State, Persistence, And Dependencies
Peer metadata is stored in `kefalnd.peer_ni`, keyed by 32-bit EFA NID address, protected by RCU plus per-peer rwlock and kref. `peer_ni_free()` removes entries unless EFALND is shutting down, decrements `peer_ni_count`, and frees via `kfree_rcu()`. The cache is in-memory only and is destroyed during base shutdown.

## Integration Points
Connection establishment uses this file for small-NID remote GID/CM-QP lookup. LNet discovery supplies remote metadata over TCP. Debugfs reads the same rhashtable. `efalnd.c` creates a self peer-NI for small local NIDs.

## Risks
The small-NID to TCP-NID derivation assumes IPv4 and same upper subnet bits. Cache keying by address means collisions are possible if generated small NIDs are not unique. Metadata lookup can block connection establishment for the TCP ping timeout. Updating peer entries races with debug reads and connection reads, so rwlock/RCU use must remain correct. `PTR_ERR(NULL)` patterns require care when helpers can return NULL.

## Test Signals
Tests should cover cache hit/miss, TCP metadata discovery success/failure/timeout, multiple returned mappings, non-EFALND mappings, self metadata publication, concurrent lookup/update/free, shutdown while lookups are in flight, and small-NID derivation from representative IP/device values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_peerni.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_proto.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_proto.h

## Purpose
This private header defines the EFALND wire protocol: completion status codes, metadata entries, QP descriptors, RDMA descriptors, connection handshake messages, data-transfer messages, common headers, protocol versions, and message type IDs.

## Important APIs, Types, And Functions
`enum kefa_comp_status` maps remote completion/error outcomes. Packed structs include `kefa_nid_md_entry`, `kefa_qp_proto`, `kefa_rdma_desc`, v2 immediate/PUTR/GETR request bodies, `kefa_getr_ack_msg`, `kefa_completion_msg`, connection probe/response/request/ack payloads, `kefa_msg_v1`, `kefa_msg_v2`, `kefa_hdr`, and top-level `kefa_msg`. Constants define magic (`EFALND_MSG_MAGIC`), protocol versions 1 and 2, min/max protocol versions, and message type IDs from connection probe through GETR done.

## Control Flow
Every EFALND packet starts with `kefa_hdr`; the receiver validates magic, protocol version, type, and total byte count before interpreting the version-specific body. V1 supports only probe/probe response with legacy `lnet_nid_t` fields. V2 carries large NIDs and all data-transfer messages. RDMA flows exchange descriptors and opaque TX-index cookies, then complete with status messages.

## State, Persistence, And Dependencies
The structs are packed wire ABI and must remain stable for inter-node compatibility. There is no live state in the header. It depends on LNet header structures such as `lnet_hdr_nid16`, `lnet_nid_t`, and `struct lnet_nid`.

## Integration Points
`efalnd.c` builds/parses data messages and maps status codes to errno. `efalnd_connection.c` builds/parses handshake messages and negotiates protocol versions. `efalnd_peerni.c` uses `kefa_nid_md_entry` for metadata exchange in LNet ping replies.

## Risks
Adding fields after flexible arrays or unions would break layout; comments explicitly prohibit adding fields after several unions. Mismatched `hdr.nob` calculations can cause short-packet rejection or overread. Version negotiation must preserve V1 probe compatibility while using V2 for data traffic. Status-code mapping must stay synchronized with sender behavior.

## Test Signals
Tests should assert packed sizes/offsets, message-size calculations for every type/version, protocol min/max negotiation, malformed magic/version/length rejection, RDMA cookie round trips, and errno/status conversion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/kcompat.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/kcompat.h

## Purpose
This compatibility header provides EFALND-local shims for kernel API differences.

## Important APIs, Types, And Functions
When `HAVE_IBDEV_TO_NODE` is not defined, it defines `ibdev_to_node(struct ib_device *ibdev)`, which returns `NUMA_NO_NODE` without a parent device or `dev_to_node(parent)` otherwise.

## Control Flow
Including files get the native `ibdev_to_node()` when the kernel provides it. Older kernels compile the inline fallback and use the RDMA device's parent device to choose a NUMA node.

## State, Persistence, And Dependencies
There is no state. The header depends on RDMA `ib_verbs.h`, Linux device NUMA helpers, and the build-system feature macro.

## Integration Points
`efalnd.c` uses `ibdev_to_node()` during EFA device initialization to select a libcfs CPU partition when the NI does not specify CPTs.

## Risks
The fallback is only as accurate as the RDMA device parent relationship. If parent is absent, EFALND falls back through `NUMA_NO_NODE` and later chooses CPT 0, which can reduce locality.

## Test Signals
Build tests should cover kernels with and without `HAVE_IBDEV_TO_NODE`; runtime startup should verify CPT selection on devices with parent NUMA nodes and parentless mocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/efalnd/kcompat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/Makefile -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/Makefile

## Purpose
This Kbuild makefile builds the Cray/HPE GNI LNet Network Driver module.

## Important APIs, Types, And Functions
`obj-m += kgnilnd.o` declares the module. `kgnilnd-objs` links `gnilnd.o`, callbacks, module parameters, debug/proc/sysctl, stack, and connection objects. `ccflags-y` defines `SVN_CODE_REV` as a Kbuild string and appends `$(GNICPPFLAGS)`. `CONFIG_GCOV_PROFILE_LNET` enables `GCOV_PROFILE`.

## Control Flow
When selected by the parent `klnds/Makefile`, Kbuild compiles each listed GNILND object and links them into `kgnilnd.o`, applying GNI-specific compiler flags.

## State, Persistence, And Dependencies
No runtime state exists in the makefile. Build behavior depends on `GNICPPFLAGS`, `SVN_CODE_REV`, kernel config, and the listed GNILND source files.

## Integration Points
It is selected through `CONFIG_LNET_GNILND` and contributes the legacy GNI LND module to the LNet build.

## Risks
Missing `GNICPPFLAGS` or incompatible GNI headers can fail compilation. Removing any object from the list can drop debug, sysctl, stack, connection, or callback functionality. `SVN_CODE_REV` quoting must remain Kbuild-safe.

## Test Signals
Build tests should compile with representative GNI flags, with and without GCOV, validate all expected object files are linked, and confirm the generated module exports the expected version/debug metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/Makefile -->
