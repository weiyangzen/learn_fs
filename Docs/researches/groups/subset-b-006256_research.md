# subset-b-006256 netlink and NFC research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/af_netlink.c -->
# sources/distributed-fs/ceph-client/net/netlink/af_netlink.c

## Purpose

`af_netlink.c` is the core Linux `PF_NETLINK` socket implementation. It registers the netlink protocol family, creates user and kernel netlink sockets, manages per-protocol port ID lookup tables, multicast listener state, socket options, unicast and broadcast delivery, dump continuations, ACK/error replies, proc/BPF iteration, tap devices, and per-network-namespace proc setup.

This file is the common substrate used by rtnetlink, generic netlink, sock_diag, netfilter, xfrm, audit-style protocols, and any kernel subsystem creating a netlink kernel socket.

## Important APIs, Types, and Functions

The main persistent objects are `struct netlink_sock`, `struct netlink_table`, `struct listeners`, and the global `nl_table`. Socket creation uses `netlink_create()` for userspace sockets and `__netlink_kernel_create()` for kernel endpoints. Binding and addressing are handled by `netlink_bind()`, `netlink_connect()`, `netlink_autobind()`, `netlink_insert()`, `netlink_remove()`, and `netlink_lookup()`.

Delivery APIs include `netlink_unicast()`, `netlink_broadcast_filtered()`, `netlink_broadcast()`, `nlmsg_notify()`, `netlink_attachskb()`, `netlink_sendskb()`, and `netlink_detachskb()`. Message framing and control replies are built by `__nlmsg_put()`, `netlink_ack()`, `netlink_ack_tlv_len()`, and `netlink_ack_tlv_fill()`.

Long-running dumps use `__netlink_dump_start()` and the internal `netlink_dump()` state machine stored in `nlk->cb`. Userspace receive/send paths are `netlink_sendmsg()` and `netlink_recvmsg()`. Socket option handling lives in `netlink_setsockopt()` and `netlink_getsockopt()`.

Exported capability checks include `netlink_ns_capable()`, `netlink_capable()`, `netlink_net_capable()`, and `netlink_strict_get_check()`.

## Control Flow

Initialization runs from `netlink_proto_init()`: it registers `netlink_proto`, allocates `nl_table`, initializes one rhashtable per netlink protocol number, creates the usersock table entry, registers `PF_NETLINK`, installs pernet proc/tap operations, and calls `rtnetlink_init()`.

User socket creation validates type/protocol, optionally requests a module, captures protocol callbacks from `nl_table`, and allocates a `struct netlink_sock`. Bind either inserts an explicit `nl_pid` or autobinds to the task TGID and then negative IDs on collision. Multicast membership updates allocate the group bitmap, call protocol-specific bind/unbind hooks, maintain `subscriptions`, update `mc_list`, and refresh aggregate listener masks.

`netlink_sendmsg()` parses destination address or connected defaults, autobinds the sender if needed, allocates an skb, copies user data, runs LSM filtering, multicasts if `dst_group` is set, and unicasts to `dst_portid`. `netlink_unicast()` looks up the peer, handles direct kernel-socket callbacks, applies socket filters, performs receive-buffer backpressure in `netlink_attachskb()`, and queues to the receive queue. Broadcast walks `mc_list`, clones or references the skb per listener, filters, annotates peer netns IDs, and records congestion or delivery failures.

Dump start copies the original request skb, resolves the requester socket, installs callback state under `nl_cb_mutex`, optionally runs `control->start`, and invokes `netlink_dump()`. Each receive call can resume a running dump once receive memory drops below half the socket buffer. Completion emits `NLMSG_DONE`, optional extended ACK TLVs, calls `done`, drops the module reference, and clears `cb_running`.

## State and Persistence Behavior

Per-socket state persists in `struct netlink_sock`: `portid`, default destination, group bitmap, subscriptions, `max_recvmsg_len`, congestion bit, flags, callback state, and protocol callbacks. Per-protocol state persists in `nl_table[protocol]`: rhashtable, multicast list, listener masks, callbacks, registered count, module pointer, and group count.

The port lookup table is an RCU-protected rhashtable keyed by network namespace and port ID. Multicast listeners are kept in `mc_list` with bitmaps on each socket and an aggregate `listeners->masks` table for fast `netlink_has_listeners()`. Dump callback state persists across `recvmsg()` calls and is explicitly torn down on socket release.

Reference and lifetime management are delicate: table insertion takes a socket reference, removal drops it after rhashtable deletion, release uses `call_rcu()` to free groups and socket storage, and generic netlink release synchronization uses `genl_sk_destructing_cnt`.

## Dependencies and Integration Points

This file depends on sockets, skbuffs, rhashtable, RCU, network namespaces, procfs, BPF iterators, LSM hooks, credentials/SCM, notifier chains, and netlink policy dumping for extended ACKs. It integrates directly with `genetlink.c` through `genl_sk_destructing_cnt`, with `policy.c` via `netlink_policy_dump_attr_size_estimate()` and `netlink_policy_dump_write_attr()`, with rtnetlink through early `rtnetlink_init()`, and with netlink taps through ARPHRD_NETLINK devices.

## Risks and Edge Cases

Backpressure and congestion behavior must preserve references when sleeping and retrying delivery. Autobind races are tolerated, but port visibility relies on paired `WRITE_ONCE()`, `READ_ONCE()`, and barriers. Multicast group changes mix table locks, protocol callbacks, and RCU listener masks. Dump callbacks run under per-socket callback mutexes and module references; missing cleanup leaks skb/module state or leaves `cb_running` stuck. ACK TLV offsets must be checked against the original message payload to avoid reporting invalid pointers.

## Test Signals

Useful signals include `tools/testing/selftests/net/netlink_*`, generic netlink controller dumps (`genl ctrl list`, `nlctrl` policy dumps), `ss -A netlink`, `/proc/net/netlink`, `NETLINK_EXT_ACK` error messages, multicast membership changes, namespace multicast tests, BPF iterator build coverage, and socket diag dumps for `AF_NETLINK`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/af_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/af_netlink.h -->
# sources/distributed-fs/ceph-client/net/netlink/af_netlink.h

## Purpose

`af_netlink.h` is the private header shared by the core netlink implementation and diagnostic helpers. It defines the in-kernel layout for netlink sockets and per-protocol netlink tables, along with flag IDs and group bitmap sizing helpers.

## Important APIs, Types, and Functions

The central type is `struct netlink_sock`, which embeds `struct sock` as its first member and adds netlink-specific state: flags, local and default destination port/group, subscription counts, group bitmap, maximum observed receive length, wait queue, bound/callback booleans, dump callback object, callback mutex, protocol callbacks, module owner, rhashtable node, and RCU head.

`nlk_sk()` converts from `struct sock *` to `struct netlink_sock *`, and `nlk_test_bit()` reads one of the private `NETLINK_F_*` flags. `struct netlink_table` describes one protocol number: its rhashtable, multicast listener list, RCU listener mask table, group count, callbacks, module, and registration count.

## Control Flow

The header has no executable control flow, but it fixes the object model used by `af_netlink.c` and `diag.c`. Creation initializes `netlink_sock` fields after `sk_alloc()`. Hash insertion uses `node`. Multicast operations use `groups` and `subscriptions`. Dump operations mutate `cb`, `cb_running`, `dump_done_errno`, and `nl_cb_mutex`.

## State and Persistence Behavior

All fields in `struct netlink_sock` are per-socket persistent state. `struct netlink_table` is global protocol persistent state referenced through exported `nl_table` under `nl_table_lock` plus RCU. The first-member embedding of `struct sock` is a hard ABI assumption for casting and allocation.

## Dependencies and Integration Points

The header depends on `linux/rhashtable.h`, `linux/atomic.h`, and `net/sock.h`. `diag.c` uses it to inspect private socket state. `af_netlink.c` owns allocation, synchronization, and mutation of these objects. Generic netlink also depends indirectly on the registered table callbacks stored here.

## Risks and Edge Cases

Changing field layout can break container casts, diagnostic assumptions, or BPF/proc observation. Adding flags requires keeping `NETLINK_F_*` numbering aligned with option handling and diagnostic flag export. Group bitmap sizing through `NLGRPSZ()` and `NLGRPLONGS()` must remain consistent with both allocation and user-visible group dumps.

## Test Signals

Build coverage of `af_netlink.c`, `diag.c`, and generic netlink is the primary signal. Runtime checks include successful `AF_NETLINK` socket creation, multicast group subscription, `/proc/net/netlink` output, and sock_diag reporting of flags/groups.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/af_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/diag.c -->
# sources/distributed-fs/ceph-client/net/netlink/diag.c

## Purpose

`diag.c` implements the `sock_diag` handler for `AF_NETLINK`. It lets userspace dump netlink sockets, their protocol, state, port IDs, multicast memberships, memory information, flags, inode, and socket cookie.

## Important APIs, Types, and Functions

`sk_diag_fill()` builds one `SOCK_DIAG_BY_FAMILY` reply containing `struct netlink_diag_msg`. Optional attributes come from `sk_diag_dump_groups()`, `sock_diag_put_meminfo()`, and `sk_diag_put_flags()`. `__netlink_diag_dump()` walks one netlink protocol table, first through its rhashtable and then through multicast-only sockets in `mc_list`. `netlink_diag_dump()` handles either a single protocol or `NDIAG_PROTO_ALL`. `netlink_diag_handler_dump()` validates requests and starts a dump through `netlink_dump_start()`.

## Control Flow

A sock_diag request reaches `netlink_diag_handler_dump()`. Only dump requests are supported; non-dump requests return `-EOPNOTSUPP`. For each selected protocol, `__netlink_diag_dump()` creates or reuses an rhashtable iterator in `cb->args[2]`, emits matching sockets in the caller's network namespace, exits that walk, and then scans `mc_list` for bound but unhashed multicast sockets. Iteration positions are persisted in `cb->args[0]` and `cb->args[1]` across dump calls.

## State and Persistence Behavior

The module does not own long-lived socket state. It reads `struct netlink_sock` state from `af_netlink.h` and stores temporary dump cursor state in `netlink_callback` arguments. `netlink_diag_dump_done()` exits any active hash walk and frees the iterator.

## Dependencies and Integration Points

The file integrates with `sock_diag_register()`, `netlink_dump_start()`, rhashtable walking, `nl_table`, `nl_table_lock`, and netlink private socket layout. The module alias advertises diagnostic support for `PF_NETLINK`, `NETLINK_SOCK_DIAG`, and `AF_NETLINK`.

## Risks and Edge Cases

The two-phase walk is easy to break: rhashtable iterators must be exited exactly once, and `mc_list` must be protected by `nl_table_lock`. Namespace filtering avoids leaking sockets across namespaces. Optional attributes can overrun the skb; callers signal partial progress by returning `skb->len` so the dump can continue.

## Test Signals

Run `ss -A netlink`, `ss -a -f netlink`, or sock_diag-based tests while sockets are bound to groups and while a dump callback is running. Verify `NDIAG_SHOW_GROUPS`, `NDIAG_SHOW_MEMINFO`, and `NDIAG_SHOW_FLAGS` attributes and module load/unload behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/genetlink.c -->
# sources/distributed-fs/ceph-client/net/netlink/genetlink.c

## Purpose

`genetlink.c` implements Generic Netlink on top of the core netlink socket layer. It registers generic netlink families, validates and dispatches family operations, manages multicast group IDs, exposes the `nlctrl` controller family, supports policy dumping, per-socket family-private storage, per-network-namespace generic netlink sockets, and all-namespace multicast helpers.

## Important APIs, Types, and Functions

Family registry state is held in `genl_fam_idr`; multicast group allocation is tracked in `mc_groups`. Synchronization uses `genl_mutex` for serialized processing and `cb_lock` to coordinate callbacks/unregistration.

Public APIs include `genl_register_family()`, `genl_unregister_family()`, `genlmsg_put()`, `genl_sk_priv_get()`, `__genl_sk_priv_get()`, `genlmsg_multicast_allns()`, and `genl_notify()`. Operation lookup and normalization use `genl_get_cmd()`, `genl_get_cmd_full()`, `genl_get_cmd_small()`, `genl_get_cmd_split()`, `genl_cmd_full_to_split()`, and `genl_op_iter`.

Message processing flows through `genl_rcv()`, `genl_rcv_msg()`, `genl_family_rcv_msg()`, `genl_family_rcv_msg_doit()`, and `genl_family_rcv_msg_dumpit()`. Controller commands are implemented by `ctrl_getfamily()`, `ctrl_dumpfamily()`, `ctrl_dumppolicy_start()`, `ctrl_dumppolicy()`, and `ctrl_dumppolicy_done()`.

## Control Flow

`genl_init()` first registers the controller family, then registers pernet generic netlink sockets. Each namespace gets `net->genl_sock` via `netlink_kernel_create()` with `genl_rcv`, bind, unbind, and release hooks.

Family registration validates operation arrays, reserves or allocates a family ID, validates multicast groups, expands netlink group bitmaps, unlocks, and broadcasts controller notifications. Unregistration removes multicast users from all namespaces, clears group IDs, removes the family from the IDR, waits for generic netlink sockets currently destructing, frees per-socket private xarrays, and emits a delete event.

Receive dispatch runs under `cb_lock`; non-parallel families also take `genl_mutex`. The generic netlink header is checked, the requested command is resolved to either a `doit` or `dumpit` operation based on `NLM_F_DUMP`, permissions are enforced, attributes are parsed against the selected policy, and the family callback is called. Dumps wrap family callbacks in core netlink dump control callbacks so operation-specific `start`, `dumpit`, and `done` get consistent `genl_info`.

The controller family reports family metadata, command capabilities, multicast groups, and policies. Policy dumps first build a policy index map using `policy.c`, then emit per-command policy index references followed by policy attribute descriptions.

## State and Persistence Behavior

Registered families persist in `genl_fam_idr` until unregistered. Each family stores assigned `id` and `mcgrp_offset`. Optional per-socket private data persists in an xarray keyed by socket pointer and is freed from the generic netlink release hook. Multicast group bitmaps persist globally and drive `af_netlink.c` group counts.

Dump state persists in allocated `struct genl_dumpit_info` and controller policy context stored in `netlink_callback`. Command validation defaults reserved future operations without explicit policy to a reject-all policy, which is a persistent safety behavior for families that set `resv_start_op`.

## Dependencies and Integration Points

Generic netlink depends on `af_netlink.c` for kernel sockets, multicast delivery, dump lifecycle, group resizing, and socket release callbacks. It depends on `policy.c` for `CTRL_CMD_GETPOLICY`. It exposes family metadata to userspace through `nlctrl` and to modules through exported Generic Netlink APIs. Family callbacks integrate with capability helpers in `af_netlink.c` and with net namespace state through `genl_info_net_set()`.

## Risks and Edge Cases

Family unregistration must not race with live callbacks or destructing sockets. Split operation arrays must be sorted and have exactly one DO or DUMP capability per entry. Legacy validation flags can disable strict parsing, so new operations should use explicit policy and reserved operation boundaries. Multicast group allocation has historical reserved IDs and must resize group maps across namespaces without assuming rollback is complete on allocation failure. Controller policy dumping can return partial skbs and must keep cursor state consistent.

## Test Signals

Useful signals include `genl ctrl list`, `genl ctrl get name nlctrl`, `CTRL_CMD_GETPOLICY` userspace queries, module load/unload for a generic netlink family, namespace multicast tests, capability-gated multicast binding, family private socket storage tests, and build coverage for families using full, small, and split operation tables.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/genetlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/genetlink.h -->
# sources/distributed-fs/ceph-client/net/netlink/genetlink.h

## Purpose

`genetlink.h` is a small private synchronization header shared between Generic Netlink and the core netlink release path. It declares state used to wait for generic netlink socket destruction during family unregistration.

## Important APIs, Types, and Functions

The header declares `atomic_t genl_sk_destructing_cnt` and `wait_queue_head_t genl_sk_destructing_waitq`. `af_netlink.c` increments and decrements the counter around `NETLINK_GENERIC` socket removal/release, and `genetlink.c` waits on the queue during `genl_unregister_family()`.

## Control Flow

There is no executable code. The control flow is cross-file: `netlink_remove()` increments the counter for generic netlink sockets, `netlink_release()` decrements it and wakes the queue when it reaches zero, and `genl_unregister_family()` waits after removing a family from the IDR before freeing family-private socket storage.

## State and Persistence Behavior

The counter is global process state and persists for the life of the generic netlink subsystem. It represents in-flight generic netlink socket destruction, not registered family count.

## Dependencies and Integration Points

The header depends on `linux/wait.h`. Its only integration point is synchronization between `af_netlink.c` and `genetlink.c`.

## Risks and Edge Cases

If the counter is not balanced, family unregistration can hang forever or free per-socket private storage while release still needs it. The wake queue must be signaled only after the last in-flight generic netlink socket release completes.

## Test Signals

Stress generic netlink family unregister while user sockets are closing, with lockdep and refcount debugging enabled. Module unload tests for families using `sock_priv_size` exercise this path.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/genetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/policy.c -->
# sources/distributed-fs/ceph-client/net/netlink/policy.c

## Purpose

`policy.c` converts kernel `struct nla_policy` arrays into netlink-advertised policy descriptions. It is used by extended ACK reporting and Generic Netlink `CTRL_CMD_GETPOLICY` so userspace can inspect expected attribute types, nested policies, ranges, masks, and length constraints.

## Important APIs, Types, and Functions

`struct netlink_policy_dump_state` stores a linear table of unique policy pointer plus maxattr pairs and cursor fields `policy_idx` and `attr_idx`. Public APIs are `netlink_policy_dump_add_policy()`, `netlink_policy_dump_get_policy_idx()`, `netlink_policy_dump_loop()`, `netlink_policy_dump_attr_size_estimate()`, `netlink_policy_dump_write_attr()`, `netlink_policy_dump_write()`, and `netlink_policy_dump_free()`.

Internal helpers include `alloc_state()`, `add_policy()`, `netlink_policy_dump_finished()`, and `__netlink_policy_dump_write_attr()`.

## Control Flow

Dump setup calls `netlink_policy_dump_add_policy()` with one or more root policies. It allocates state on first use, adds the root policy, then walks every registered policy looking for `NLA_NESTED` and `NLA_NESTED_ARRAY` entries and appends those nested policies as additional indexed entries. This produces a stable index table for the dump.

Output code repeatedly calls `netlink_policy_dump_loop()` and `netlink_policy_dump_write()`. `netlink_policy_dump_write()` emits one non-empty attribute description per call, skipping `NLA_UNSPEC` and `NLA_REJECT`, and advances the policy and attribute cursor. Attribute output records the normalized netlink policy type plus optional nested policy index, numeric min/max, masks, bitfield masks, or string/binary length constraints.

## State and Persistence Behavior

Dump state is per-dump heap memory. It persists only between netlink dump callbacks and is freed by the caller through `netlink_policy_dump_free()`. It references static policy arrays owned by netlink families; it does not copy policies.

## Dependencies and Integration Points

The file depends on netlink attribute policy definitions and range helpers from `<net/netlink.h>`. `genetlink.c` uses it for controller policy dumps, and `af_netlink.c` uses attribute size estimation and single-attribute output for extended ACK policy TLVs.

## Risks and Edge Cases

Policy identity is pointer plus maxattr, so dynamically allocated policies must remain alive for the whole dump. Nested policy discovery can reallocate state, and failure semantics try to preserve caller-visible state only when a state already existed. Output intentionally skips reject/unspecified entries; callers must tolerate `-ENODATA` as "nothing useful to emit." Size estimates must stay in sync with emitted attributes or ACK allocation can be too small.

## Test Signals

Use `CTRL_CMD_GETPOLICY` against families with nested attributes, arrays, masks, signed and unsigned ranges, strings, binaries, flags, and bitfield32 attributes. Extended ACK tests with bad attributes should include `NLMSGERR_ATTR_POLICY` output when `NETLINK_EXT_ACK` is enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlink/policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/Kconfig -->
# sources/distributed-fs/ceph-client/net/nfc/Kconfig

## Purpose

This Kconfig file defines the top-level NFC subsystem options. It enables the core NFC module, the optional digital protocol stack, and includes NCI, HCI, and driver-specific NFC configuration trees.

## Important APIs, Types, and Functions

The options are `NFC` and `NFC_DIGITAL`. `NFC` is a tristate menu option depending on `RFKILL || !RFKILL` and builds the core module named `nfc`. `NFC_DIGITAL` depends on `NFC`, selects `CRC_CCITT` and `CRC_ITU_T`, and builds the `nfc_digital` module. The file sources `net/nfc/nci/Kconfig`, `net/nfc/hci/Kconfig`, and `drivers/nfc/Kconfig`.

## Control Flow

Kconfig selection controls which Makefile objects are built. Enabling `NFC` exposes the subsystem and lower-level protocol stacks. Enabling `NFC_DIGITAL` pulls CRC helpers needed by `digital_core.c`, `digital_dep.c`, and `digital_technology.c`.

## State and Persistence Behavior

There is no runtime state. Configuration state persists in the kernel build configuration and determines module availability and compile-time dependencies.

## Dependencies and Integration Points

This file integrates NFC core with RFKILL, the digital stack, NCI, HCI, and NFC device drivers. The selected CRC libraries are required by the digital stack's CRC-A, CRC-B, and CRC-F helpers.

## Risks and Edge Cases

Missing CRC selects would break the digital stack at link time. Driver Kconfig entries are sourced only through this menu, so disabling `NFC` hides downstream NFC drivers and protocol stacks.

## Test Signals

Build matrix coverage should include `CONFIG_NFC=m/y`, `CONFIG_NFC_DIGITAL=m/y`, RFKILL enabled and disabled, plus NCI/HCI driver combinations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/Makefile -->
# sources/distributed-fs/ceph-client/net/nfc/Makefile

## Purpose

This Makefile maps NFC Kconfig symbols to built objects and module composition. It builds the NFC core module, optional NCI and HCI subdirectories, and the digital protocol stack module.

## Important APIs, Types, and Functions

`obj-$(CONFIG_NFC) += nfc.o` builds the core NFC module. `nfc-objs` includes `core.o`, `netlink.o`, `af_nfc.o`, `rawsock.o`, and LLCP implementation files. `obj-$(CONFIG_NFC_DIGITAL) += nfc_digital.o` builds `digital_core.o`, `digital_technology.o`, and `digital_dep.o`. `obj-$(CONFIG_NFC_NCI)` and `obj-$(CONFIG_NFC_HCI)` descend into subdirectories.

## Control Flow

The build system links object lists into modules based on configuration. Core NFC initialization in `core.c` expects raw socket, LLCP, netlink, and PF_NFC pieces to be present in the same `nfc` module.

## State and Persistence Behavior

There is no runtime state. Build state is the selected module composition.

## Dependencies and Integration Points

The object grouping ties `af_nfc.c` socket family registration, `core.c` device lifecycle, NFC generic netlink, raw sockets, and LLCP into one module. The digital module depends on exported NFC core APIs and CRC helpers selected by Kconfig.

## Risks and Edge Cases

Moving objects between modules would require checking exported symbols and initialization order. Omitting `af_nfc.o`, `rawsock.o`, or LLCP files from `nfc-objs` would break public PF_NFC socket functionality or LLCP support.

## Test Signals

Build `CONFIG_NFC=m`, verify `nfc.ko` contains core, netlink, PF_NFC, raw socket, and LLCP symbols, and build `CONFIG_NFC_DIGITAL=m` to verify `nfc_digital.ko` links against exported NFC core APIs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/af_nfc.c -->
# sources/distributed-fs/ceph-client/net/nfc/af_nfc.c

## Purpose

`af_nfc.c` registers the `PF_NFC` socket family and dispatches NFC socket creation to protocol-specific implementations such as raw sockets and LLCP.

## Important APIs, Types, and Functions

The file maintains `proto_tab[NFC_SOCKPROTO_MAX]` protected by `proto_tab_lock`. `nfc_sock_create()` is the family create callback. `nfc_proto_register()` and `nfc_proto_unregister()` are exported protocol registration APIs. `af_nfc_init()` registers the socket family, and `af_nfc_exit()` unregisters it.

## Control Flow

Core NFC initialization calls `af_nfc_init()`, which registers `nfc_sock_family_ops`. When userspace creates a `PF_NFC` socket, `nfc_sock_create()` rejects non-init network namespaces, validates the protocol number, takes a read lock, tries to pin the registered protocol module, and calls that protocol's create callback. Protocol modules register by first registering their `struct proto`, then inserting the protocol descriptor into `proto_tab` under the write lock.

## State and Persistence Behavior

The protocol table persists for the life of the NFC core module. Entries are added by protocols at initialization and cleared at exit. Module references are held only around create callback invocation.

## Dependencies and Integration Points

This file integrates with Linux socket family registration, `struct nfc_protocol` from NFC internals, and protocol implementations built into `nfc.o` such as raw sockets and LLCP sockets.

## Risks and Edge Cases

Only `init_net` is supported; namespace support changes would need broader NFC core review. Registration must unwind `proto_register()` on table conflicts. A protocol ID outside the table is `-EINVAL`, while an unregistered valid protocol is `-EPROTONOSUPPORT`.

## Test Signals

Create raw and LLCP NFC sockets with registered protocols, try invalid protocol IDs, verify behavior in non-init network namespaces, and exercise module unload after sockets are created and closed.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/af_nfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/core.c -->
# sources/distributed-fs/ceph-client/net/nfc/core.c

## Purpose

`core.c` is the NFC subsystem device and lifecycle manager. It allocates/registers NFC devices, controls device up/down and polling, manages targets and secure elements, coordinates DEP links and target-mode activation, integrates rfkill, emits generic netlink notifications, owns presence checking timers, and initializes the NFC core module.

## Important APIs, Types, and Functions

Device lifecycle APIs include `nfc_allocate_device()`, `nfc_register_device()`, `nfc_unregister_rfkill()`, `nfc_remove_device()`, `nfc_unregister_device()`, and the release path `nfc_release()`. Operational APIs include `nfc_fw_download()`, `nfc_dev_up()`, `nfc_dev_down()`, `nfc_start_poll()`, `nfc_stop_poll()`, `nfc_activate_target()`, `nfc_deactivate_target()`, `nfc_data_exchange()`, `nfc_dep_link_up()`, `nfc_dep_link_down()`, and `nfc_dep_link_is_up()`.

Target and SE APIs include `nfc_targets_found()`, `nfc_target_lost()`, `nfc_add_se()`, `nfc_remove_se()`, `nfc_enable_se()`, `nfc_disable_se()`, `nfc_se_transaction()`, and `nfc_se_connectivity()`. Target mode and LLCP hooks include `nfc_tm_activated()`, `nfc_tm_deactivated()`, `nfc_tm_data_received()`, `nfc_set_remote_general_bytes()`, and `nfc_get_local_general_bytes()`.

## Control Flow

`nfc_init()` registers the NFC class, generic netlink interface, raw sockets, LLCP, and PF_NFC socket family in that order. Device allocation validates required driver operations, allocates an ID from `nfc_index_ida`, initializes a class device, stores driver ops/protocols/headroom, initializes generic netlink per-device data, secure-element list, target generation, and optional presence timer/work.

Most operations take `device_lock(&dev->dev)`, reject `shutting_down`, and enforce state transitions. `nfc_dev_up()` checks rfkill and firmware download state before calling driver `dev_up` and optionally discovering secure elements. Polling starts only when the device is up and not already polling, calls driver `start_poll`, and records polling state. Target discovery from drivers assigns target IDs, replaces the target array, bumps generation, clears polling, and sends generic netlink notifications.

Initiator data exchange verifies the active target, pauses presence checking around driver `im_transceive`, and restores the timer. Target mode sends through `tm_send`. DEP link-up obtains LLCP general bytes, calls driver `dep_link_up`, and later `nfc_dep_link_is_up()` marks state and notifies LLCP/genl. Unregister first marks rfkill/shutdown and notifies userspace, then cancels timers/work, unregisters LLCP, removes the device, and release frees targets, secure elements, genl data, IDA ID, and the device.

## State and Persistence Behavior

Persistent device state includes `dev_up`, `polling`, `active_target`, `dep_link_up`, `rf_mode`, target array and generation, secure-element list and state, rfkill pointer, firmware-download flag, `shutting_down`, and optional presence timer/work. Global state includes `nfc_devlist_generation`, `nfc_devlist_mutex`, `nfc_index_ida`, and the exported `nfc_class`.

Targets are replaced as a batch on discovery and compacted on loss. Secure elements are list entries owned by the device. Presence checking periodically calls driver `check_presence` and emits target-lost notifications on failure.

## Dependencies and Integration Points

The core depends on rfkill, the device model, generic netlink NFC notifications, LLCP, raw sockets, PF_NFC sockets, skbuff allocation helpers, IDA, timers, and driver-provided `struct nfc_ops`. Digital, NCI, HCI, and hardware drivers call into these exported APIs.

## Risks and Edge Cases

State transitions rely on `device_lock`; driver callbacks must not call back in ways that deadlock. Presence timers must be deleted around transceive/deactivate/unregister. Firmware download, rfkill, polling, and active target state are mutually constrained. `nfc_targets_found()` must not be called from atomic context but uses `GFP_ATOMIC` for target duplication. Shutdown ordering must prevent userspace notifications or LLCP callbacks after device removal.

## Test Signals

Use NFC generic netlink commands for device add/remove, up/down, polling, target discovery/loss, DEP link up/down, secure element add/remove/enable/disable, rfkill block/unblock, and firmware download completion. Driver fault injection should cover `check_presence`, polling errors, and unregister during active work.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/digital.h -->
# sources/distributed-fs/ceph-client/net/nfc/digital.h

## Purpose

`digital.h` is the private header for the NFC Digital Protocol stack. It declares command types, protocol constants, CRC helpers, command-queue APIs, initiator polling APIs, target listen APIs, NFC-DEP data exchange entry points, and shared data-exchange callback state.

## Important APIs, Types, and Functions

Important definitions include `DIGITAL_CMD_IN_SEND`, `DIGITAL_CMD_TG_SEND`, `DIGITAL_CMD_TG_LISTEN`, `DIGITAL_CMD_TG_LISTEN_MDAA`, `DIGITAL_CMD_TG_LISTEN_MD`, maximum digital header/CRC lengths, NFC-DEP SENS/SEL constants, and driver CRC capability macros.

`struct digital_data_exch` stores an NFC core data-exchange callback and context. Declared functions include `digital_skb_alloc()`, `digital_send_cmd()`, `digital_poll_next_tech()`, initiator technology probes, target discovery, ISO-DEP SOD helpers, NFC-DEP ATR/DEP request/responses, target listen handlers, and generic CRC helpers.

## Control Flow

The header ties `digital_core.c`, `digital_dep.c`, and `digital_technology.c` together. Inline wrappers route initiator send, target send, and target listen operations into the common command queue. CRC inline wrappers bind CRC-A, CRC-B, CRC-F, or no-CRC behavior to the generic `digital_skb_add_crc()` and `digital_skb_check_crc()`.

## State and Persistence Behavior

The header itself owns no state, but it defines constants and callback/context shapes used by persistent `struct nfc_digital_dev` state: current CRC handlers, RF technology, command queue, DEP payload/chaining state, and data-exchange callbacks.

## Dependencies and Integration Points

It depends on public NFC headers, digital driver APIs, `crc-ccitt`, and `crc-itu-t`. It is the shared contract between the digital core, protocol activation logic, technology polling/listening code, and lower-level NFC digital drivers.

## Risks and Edge Cases

CRC helper selection must match RF technology and driver capabilities. Command type constants must match `digital_wq_cmd()` dispatch. Header and tailroom constants influence skb allocation in `nfc_digital_allocate_device()`; underestimating them can corrupt packet construction.

## Test Signals

Build `CONFIG_NFC_DIGITAL` with drivers that both do and do not advertise CRC offload. Exercise initiator and target paths for NFC-A, NFC-B, NFC-F, ISO15693, ISO-DEP, and NFC-DEP to verify the declared cross-file APIs remain consistent.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/digital.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/digital_core.c -->
# sources/distributed-fs/ceph-client/net/nfc/digital_core.c

## Purpose

`digital_core.c` is the framework glue for NFC Digital Protocol devices. It provides skb allocation and CRC helpers, serializes driver commands through workqueues, implements polling orchestration, exposes NFC core operations for digital devices, and allocates/registers/unregisters `struct nfc_digital_dev`.

## Important APIs, Types, and Functions

`struct digital_cmd` is the queued command object. Command helpers include `digital_send_cmd()`, `digital_wq_cmd()`, `digital_send_cmd_complete()`, and `digital_wq_cmd_complete()`. CRC helpers are `digital_skb_add_crc()` and `digital_skb_check_crc()`.

Polling and target setup use `digital_start_poll()`, `digital_stop_poll()`, `digital_poll_next_tech()`, `digital_wq_poll()`, `digital_add_poll_tech()`, and `digital_target_found()`. NFC core operation implementations include `digital_dev_up()`, `digital_dev_down()`, `digital_dep_link_up()`, `digital_dep_link_down()`, `digital_activate_target()`, `digital_deactivate_target()`, `digital_in_send()`, and `digital_tg_send()`.

Device APIs exported to drivers are `nfc_digital_allocate_device()`, `nfc_digital_free_device()`, `nfc_digital_register_device()`, and `nfc_digital_unregister_device()`.

## Control Flow

Drivers allocate a digital device with required `nfc_digital_ops`. The allocator validates callbacks, records capabilities, initializes command and poll work, maps supported NFC protocols, reserves extra head/tailroom for digital headers and CRC, allocates an NFC core device, and stores `ddev` as driver data.

Commands are queued by `digital_send_cmd()`. `digital_wq_cmd()` picks the first non-pending command, marks it pending, logs TX data, dispatches to the proper driver operation based on command type, and lets the driver complete asynchronously through `digital_send_cmd_complete()`. Completion schedules `digital_wq_cmd_complete()`, which removes the command, logs RX data, invokes the original digital callback, frees command resources, and schedules the next command.

Polling builds a randomized table of matching initiator and target technologies. `digital_wq_poll()` invokes the selected technology probe/listen function; failures call `digital_poll_next_tech()` to switch RF off, pick another technology, and reschedule after a short interval. `digital_target_found()` selects framing and CRC functions based on detected protocol and RF technology, configures hardware framing, clears polling count, and reports the target to NFC core.

Data exchange adds protocol-specific wrappers: NFC-DEP goes to `digital_in_send_dep_req()`, ISO-DEP pushes/pulls PCB bytes, other protocols add/check CRC and send a normal initiator command. Target mode sends DEP responses.

## State and Persistence Behavior

Persistent digital state includes command queue, command work items, polling technology table/index/count, current protocol, current RF technology, current NFC-DEP PNI, target FSC, selected CRC function pointers, and driver capability flags. `poll_tech_count` doubles as the active polling marker. Unregistration cancels work and flushes queued commands with `ERR_PTR(-ENODEV)` callbacks.

## Dependencies and Integration Points

The file integrates public NFC core operations with lower-level digital drivers through `struct nfc_digital_ops`. It depends on `digital_dep.c` for NFC-DEP and `digital_technology.c` for RF technology discovery and target listen flows.

## Risks and Edge Cases

The command queue assumes one active driver command at a time. A driver that fails to complete a command can stall the queue. Unregister must cancel work and call callbacks so owners can free buffers. Polling state is shared between workqueue callbacks and stop/unregister paths, so lock ordering around `poll_lock` matters. CRC function selection must match driver offload flags or frames will be rejected.

## Test Signals

Use a digital-capable NFC driver or simulator to exercise start/stop poll, RF cycling, technology fallback, target activation, transceive, target mode send, unregister during pending commands, and both CRC-offload and software-CRC modes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/digital_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/digital_dep.c -->
# sources/distributed-fs/ceph-client/net/nfc/digital_dep.c

## Purpose

`digital_dep.c` implements NFC-DEP activation and data exchange for the NFC Digital stack. It handles ATR_REQ/ATR_RES activation, optional PSL_REQ/PSL_RES speed/payload negotiation, DEP_REQ/DEP_RES transport, payload chaining, PNI tracking, ACK/NACK, ATN, RTOX timeout extension, DID checks, and initiator/target role differences.

## Important APIs, Types, and Functions

Protocol structures include `digital_atr_req`, `digital_atr_res`, `digital_psl_req`, `digital_psl_res`, and `digital_dep_req_res`. Key exported entry points are `digital_in_send_atr_req()`, `digital_in_send_dep_req()`, `digital_tg_recv_atr_req()`, and `digital_tg_send_dep_res()`.

Shared helpers include `digital_skb_push_dep_sod()`, `digital_skb_pull_dep_sod()`, `digital_send_dep_data_prep()`, `digital_recv_dep_data_gather()`, payload-size mapping helpers, initiator ACK/NACK/ATN/RTOX resend helpers, and target ACK/ATN/saved-skb helpers.

## Control Flow

Initiator activation sends ATR_REQ with NFCID3, payload-size bits, and optional general bytes. `digital_in_recv_atr_res()` validates CRC and start-of-data, extracts waiting time and remote payload size, stores remote general bytes, optionally sends PSL_REQ to switch to 424F when supported, and calls `nfc_dep_link_is_up()`.

Initiator data exchange wraps outgoing data in DEP_REQ, sets PNI, fragments if larger than `remote_payload_max`, saves a copy for retransmission, and sends. `digital_in_recv_dep_res()` validates SOD/CRC/header/DID/NAD/PNI, handles I-PDU data and chained response gathering, handles ACKs by sending the next chained fragment, rejects NACK responses, replies to RTOX requests, retransmits saved skbs on ATN, and retries NACK/ATN on timeout or I/O errors.

Target activation receives ATR_REQ, determines RF technology from SOD, validates DID and payload size, configures activated framing, sends ATR_RES with local general bytes and payload capabilities, notifies NFC core target mode activation, and then listens for PSL or DEP. PSL requests can reconfigure RF technology and framing before continuing DEP receive.

Target data exchange receives DEP_REQ, validates DID/NAD/PNI, gathers chained input with ACKs, passes completed data to `nfc_tm_data_received()`, sends DEP_RES responses from NFC core, handles incoming ACK/NACK for chained target responses, and handles ATN by resending saved data or sending an ATN response.

## State and Persistence Behavior

The file mutates persistent `nfc_digital_dev` fields: `local_payload_max`, `remote_payload_max`, `dep_rwt`, `curr_nfc_dep_pni`, `curr_rf_tech`, `curr_protocol`, `did`, `saved_skb`, `chaining_skb`, `data_exch`, `nack_count`, and `atn_count`. `saved_skb` preserves the last sent PDU for retransmission. `chaining_skb` stores remaining outgoing data or accumulated incoming data across multiple command completions.

## Dependencies and Integration Points

It depends on digital core command dispatch and CRC function pointers, NFC core DEP and target-mode notifications, LLCP general bytes through core APIs, and RF/framing configuration callbacks in the digital driver. `digital_technology.c` discovers NFC-DEP-capable targets and starts target listening before this file takes over activation.

## Risks and Edge Cases

PNI sequencing, saved-skb lifetime, and chained skb ownership are the highest-risk areas. Error paths must free `data_exch`, `saved_skb`, and `chaining_skb` exactly once. DID and NAD handling is intentionally restrictive. Payload-size negotiation must reject invalid values. RTOX multiplication is bounded by the max waiting time. Some code paths pass `NULL` callback contexts in target mode, so helper behavior must match role.

## Test Signals

Exercise NFC-DEP initiator and target activation, ATR with and without general bytes, PSL to 424F, chained payloads in both directions, ACK/NACK retries, timeout ATN behavior, RTOX handling, DID mismatch rejection, CRC failure, and unregister during pending DEP exchange.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/digital_dep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/digital_technology.c -->
# sources/distributed-fs/ceph-client/net/nfc/digital_technology.c

## Purpose

`digital_technology.c` implements NFC Digital RF technology discovery and listen flows outside the NFC-DEP transport itself. It probes initiator technologies NFC-A, NFC-B, NFC-F, and ISO15693, performs anti-collision and activation steps for Type 1/2/3/4/5 style targets, handles MIFARE response quirks, and implements target-mode listening responses for NFC-A and NFC-F before handing off to NFC-DEP activation.

## Important APIs, Types, and Functions

Initiator entry points are `digital_in_send_sens_req()`, `digital_in_send_sensb_req()`, `digital_in_send_sensf_req()`, `digital_in_send_iso15693_inv_req()`, and `digital_in_recv_mifare_res()`. ISO-DEP helpers are `digital_in_iso_dep_pull_sod()` and `digital_in_iso_dep_push_sod()`.

NFC-A anti-collision uses `digital_in_send_sdd_req()`, `digital_in_recv_sdd_res()`, `digital_in_send_sel_req()`, `digital_in_recv_sel_res()`, `digital_in_send_rats()`, and `digital_in_recv_ats()`. NFC-B activation uses SENSB and ATTRIB helpers. Target-mode functions include `digital_tg_listen_nfca()`, `digital_tg_listen_nfcf()`, `digital_tg_recv_sens_req()`, `digital_tg_recv_sensf_req()`, `digital_tg_recv_md_req()`, and the static SENS/SDD/SEL/SENSF response builders.

## Control Flow

For NFC-A polling, the stack configures 106A short framing, sends SENS_REQ, validates SENS_RES, then either reports a Jewel target or starts SDD anti-collision. SDD responses append NFCID1 fragments after BCC validation; SEL_REQ selects cascade levels; SEL_RES decides MIFARE, NFC-DEP, or Type 4A. Type 4A sends RATS and uses ATS to set FSC before reporting ISO14443.

For NFC-B, the stack configures 106B, sends SENSB_REQ, validates the response and protocol-info bits, derives FSC, sends ATTRIB_REQ, and reports ISO14443-B after validating ATTRIB_RES. For NFC-F, it sends SENSF_REQ with length prefix and optional software CRC, parses SENSF_RES, copies NFCID2 and response data, and reports either NFC-DEP or FeliCa based on NFCID2 prefix. ISO15693 sends an inventory request and reports a Type 5 target with DSFID and UID.

Target NFC-A listen configures RF/framing, waits for SENS_REQ/ALL_REQ, sends SENS_RES, receives SDD_REQ, sends random NFCID1 SDD_RES, receives SEL_REQ, sends SEL_RES advertising NFC-DEP, and waits for ATR_REQ. Target NFC-F listen validates SENSF_REQ, sends SENSF_RES with NFC-DEP NFCID2 prefix and optional request data, then dispatches follow-up ATR or SENSF requests. MDAA/MD target paths can also use driver-assisted multi-discovery and dispatch based on reported RF technology.

## State and Persistence Behavior

This file fills `struct nfc_target` fields such as SENS_RES, SEL_RES, NFCID1, NFCID2, SENSF response, ISO15693 DSFID/UID, and supported protocol. It mutates `ddev->target_fsc`, `curr_nfc_dep_pni`, and CRC behavior indirectly through `digital_target_found()`. Target-mode response builders generate random NFCIDs for listen mode.

## Dependencies and Integration Points

The file depends on digital core command scheduling, CRC helpers, driver hardware configuration, NFC core target reporting, and NFC-DEP activation in `digital_dep.c`. ISO-DEP data exchange in `digital_core.c` calls the SOD push/pull helpers here for Type 4A/B traffic.

## Risks and Edge Cases

Protocol parsing is strict and many errors fall back to the next polling technology. NFC-A cascade and BCC handling must preserve NFCID1 length correctly. ISO-DEP does not support R-blocks, S-blocks, DID, or chaining in this implementation. MIFARE ACK versus READ response requires software CRC even with driver CRC offload. Target-mode listen often ignores request content beyond minimal validation, which is appropriate for NFC-DEP advertisement but not a full tag implementation.

## Test Signals

Test polling with Type 1, MIFARE/Type 2, FeliCa/Type 3, Type 4A, Type 4B, ISO15693, and NFC-DEP peers. Include malformed SENS/SDD/SEL/ATS/ATTRIB/SENSF/inventory responses, driver CRC offload on/off, target-mode NFC-A and NFC-F listen, and ISO-DEP APDU exchange size limits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/digital_technology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/Kconfig -->
# sources/distributed-fs/ceph-client/net/nfc/hci/Kconfig

## Purpose

This Kconfig file defines the NFC HCI protocol implementation and optional SHDLC link layer support for HCI-based NFC drivers.

## Important APIs, Types, and Functions

`NFC_HCI` is a tristate option depending on `NFC` and builds the kernel NFC HCI implementation. `NFC_SHDLC` is a bool depending on `NFC_HCI`, selects `CRC_CCITT`, and enables the SHDLC link layer for HCI drivers that need it.

## Control Flow

Selecting `NFC_HCI` causes the HCI Makefile to build `hci.o`. Selecting `NFC_SHDLC` adds the SHDLC object to that module. The options are sourced from the top-level NFC Kconfig.

## State and Persistence Behavior

There is no runtime state in this file. Configuration persists in the kernel build and determines whether HCI and SHDLC code is compiled.

## Dependencies and Integration Points

HCI depends on the NFC core. SHDLC depends on HCI and CRC-CCITT. Device drivers such as PN544-style HCI frame processors rely on these symbols.

## Risks and Edge Cases

Drivers requiring SHDLC must select or depend on `NFC_SHDLC`; otherwise they can build without the needed link-layer implementation. Since `NFC_SHDLC` is bool, module/builtin combinations should be checked when HCI is modular.

## Test Signals

Build `CONFIG_NFC_HCI=m/y` with and without `CONFIG_NFC_SHDLC`, and build HCI drivers that require SHDLC to confirm dependency coverage.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/Makefile -->
# sources/distributed-fs/ceph-client/net/nfc/hci/Makefile

## Purpose

This Makefile builds the NFC HCI layer module and conditionally includes the SHDLC link-layer object.

## Important APIs, Types, and Functions

`obj-$(CONFIG_NFC_HCI) += hci.o` creates the HCI module. `hci-y` includes `core.o`, `hcp.o`, `command.o`, `llc.o`, and `llc_nop.o`. `hci-$(CONFIG_NFC_SHDLC) += llc_shdlc.o` adds SHDLC support when configured.

## Control Flow

Kbuild links the listed objects into `hci.o` when HCI support is enabled. SHDLC is compiled into the same module only when `CONFIG_NFC_SHDLC` is selected.

## State and Persistence Behavior

The file has no runtime state. It defines module composition at build time.

## Dependencies and Integration Points

The object list combines HCI core, HCP frame handling, command handling, generic LLC support, a no-op LLC backend, and optional SHDLC. The resulting module plugs into the NFC core and HCI drivers.

## Risks and Edge Cases

Missing `llc_shdlc.o` with SHDLC-enabled drivers will cause unresolved behavior or symbols depending on driver linkage. Moving objects out of `hci.o` would require reevaluating module exports and initialization order.

## Test Signals

Build with `CONFIG_NFC_HCI=m` and `CONFIG_NFC_SHDLC=y`, inspect `hci.o` composition, and load HCI drivers that use both no-op LLC and SHDLC paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/Makefile -->
