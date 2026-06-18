# Research: subset-b-005898

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/notifier.h -->
# sources/distributed-fs/ceph-client/include/linux/notifier.h

Purpose: defines the generic Linux notifier-chain API used by subsystems to publish status changes to registered callbacks without hard-coded call lists. It covers atomic, blocking, raw, and SRCU-protected chains.

Important APIs/types/functions: `struct notifier_block` carries the callback, next pointer, and priority. `struct atomic_notifier_head`, `blocking_notifier_head`, `raw_notifier_head`, and `srcu_notifier_head` encode the locking model. Initialization macros create static or dynamic heads. Register/unregister functions add and remove callbacks, call-chain functions dispatch events, robust call-chain variants roll back with a second event, and `notifier_from_errno()` / `notifier_to_errno()` map errno values to notifier return codes. `NOTIFY_DONE`, `NOTIFY_OK`, `NOTIFY_STOP`, and `NOTIFY_BAD` define callback semantics.

Control flow: a subsystem initializes a head, modules register `notifier_block` entries ordered by priority, and the owner calls the relevant `*_notifier_call_chain()` when an event occurs. Dispatch stops when a callback returns a value with `NOTIFY_STOP_MASK`. Atomic chains use a spinlock and are callable in atomic context; blocking chains use an rwsem; SRCU chains make calls cheap and unregisters expensive; raw chains require caller-provided serialization.

State and persistence: state is in-memory list membership and head locking state only. It persists for the lifetime of the head or registered module and must be torn down before callback code or backing objects disappear.

Dependencies and integration points: depends on errno, mutexes, rwsems, SRCU, spinlocks, and RCU annotations. Integration points include CPU, netdevice, reboot, suspend, VT keyboard, netlink release, NVMEM, and many other subsystem event streams.

Risks and test signals: risks include unregistering from inside a running chain, blocking inside atomic callbacks, missing SRCU cleanup, priority collisions when unique-priority registration is required, and callback lifetime races during module unload. Test signals include lockdep coverage for context misuse, notifier ordering tests, stop/errno conversion tests, robust rollback tests, and build coverage for `CONFIG_TREE_SRCU`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/notifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ns/ns_common_types.h -->
# sources/distributed-fs/ceph-client/include/linux/ns/ns_common_types.h

Purpose: centralizes common namespace type declarations and the shared `struct ns_common` layout used by cgroup, IPC, mount, network, PID, time, user, and UTS namespaces.

Important APIs/types/functions: `struct ns_common` stores namespace type, VFS stashed dentry, proc namespace operations, inode number, a main `refcount_t`, and a union containing namespace tree nodes or an RCU free head. `_Generic` macros map concrete namespace structures to their embedded `ns_common`, initial namespace object, initial inode, initial ID, proc operations, and `CLONE_NEW*` type. `FOR_EACH_NS_TYPE`, `CLONE_NS_ALL`, and `ns_common_type()` provide the canonical namespace type list.

Control flow: concrete namespace initializers and helpers use the `_Generic` macros to avoid open-coded switch statements. Consumers pass concrete namespace pointers and the macros derive common metadata, while `ns_common` itself becomes the common object for nsfs, proc, namespace trees, and lifetime management.

State and persistence: the header documents a two-tier lifetime model: `__ns_ref` controls memory lifetime and tree pinning, while `__ns_ref_active` controls user-visible active state. Initial namespaces remain active forever; non-initial namespaces can move from active to inactive and, in some cases, back to active before final destruction.

Dependencies and integration points: depends on atomic/refcount types, rbtree namespace tree types, UAPI clone flags and namespace inode/ID constants, and proc namespace operations. It integrates namespace core, nsfs, procfs, VFS dentries, and the newer namespace tree listing model.

Risks and test signals: risks include `_Generic` omissions when adding namespace types, mismatched init inode/ID constants, incorrect active-reference transitions that expose dead namespaces, and config-gated operations returning NULL unexpectedly. Test signals include namespace create/unshare/setns coverage for all `CLONE_NEW*` flags, nsfs list/open by handle tests, inactive namespace resurrection tests, and compile coverage with namespace configs disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ns/ns_common_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ns/nstree_types.h -->
# sources/distributed-fs/ceph-client/include/linux/ns/nstree_types.h

Purpose: defines the storage primitives for namespace trees: sorted red-black trees for lookup and matching lists for ordered iteration.

Important APIs/types/functions: `struct ns_tree_root` contains an `rb_root` plus `ns_list_head`. `struct ns_tree_node` contains an `rb_node` and list entry. `struct ns_tree` stores a namespace ID, active reference counter, nodes for global/per-type/owner trees, and a root for namespaces owned by the namespace.

Control flow: namespace initialization embeds an `ns_tree` in `ns_common`; namespace tree code initializes nodes, assigns IDs, inserts nodes into global and per-type roots, and removes them when reference lifetime ends. The list and rbtree represent the same ordering so lookups and sequential listns-style iteration can both be efficient.

State and persistence: state is transient kernel namespace-index state. `ns_id` and tree membership persist while the namespace is alive and tree-visible; they are not a stable on-disk identifier.

Dependencies and integration points: depends on `linux/rbtree.h` and `linux/list.h`. It is consumed by `nstree.h`, `ns_common_types.h`, and namespace lifecycle code.

Risks and test signals: risks include list/rbtree ordering divergence, double insertion/removal, ID reuse assumptions, and active reference counter misuse. Test signals include namespace creation/destruction stress, list iteration under concurrent namespace churn, lookup by ID/type, and debug checks for empty nodes after removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ns/nstree_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ns_common.h -->
# sources/distributed-fs/ceph-client/include/linux/ns_common.h

Purpose: provides namespace common lifecycle helpers, initializers, reference accessors, active-reference operations, and init namespace guards around `struct ns_common`.

Important APIs/types/functions: `__ns_common_init()`, `__ns_common_free()`, `ns_owner()`, and `may_see_all_namespaces()` are external namespace-core operations. `NS_COMMON_INIT`, `ns_common_init()`, and `ns_common_init_inum()` initialize embedded common fields. `ns_ref_read()`, `ns_ref_inc()`, `ns_ref_get()`, `ns_ref_put()`, `ns_ref_put_and_lock()`, `ns_ref_active_get()`, `ns_ref_active_put()`, and `ns_get_unless_inactive()` wrap the two-tier reference model. `is_ns_init_inum()` and `is_ns_init_id()` special-case immortal boot namespaces.

Control flow: new namespaces call `ns_common_init*()` to assign type, operations, inode, IDs, refs, and list heads. Users acquire main refs before holding a namespace internally, acquire active refs when making it visible or task/file-backed, and drop active refs before final main refs. `ns_get_unless_inactive()` gates reopening/listing paths so inactive namespaces are not exposed.

State and persistence: all state is in-memory namespace lifetime state. Initial namespace refs stay at one and are validated by warnings rather than modified; non-initial namespaces transition through active, inactive, and destroyed states according to main and active refcounts.

Dependencies and integration points: depends on `ns_common_types.h`, refcounts, VFS warning helpers, sched/nsfs UAPI constants, spinlocks, and namespace tree fields. It integrates nsfs, proc namespace operations, task namespace switching, and owner namespace lookup.

Risks and test signals: risks include leaking active references, decrementing initial namespace refs, reopening an inactive namespace, freeing while active refs remain, and confusing main refs with active visibility refs. Test signals include KASAN/refcount debug namespace lifecycle tests, setns/open file descriptor lifetime checks, pid/user namespace delayed cleanup, and namespace tree visibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ns_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nsc_gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/nsc_gpio.h

Purpose: declares the common file-operation helper interface for National Semiconductor GPIO controllers used by Geode and PC-8736x style chips.

Important APIs/types/functions: `struct nsc_gpio_ops` supplies controller-specific methods for configuration, dumping state, get/set/change/current pin state, module ownership, and a device pointer for debug output. `nsc_gpio_read()`, `nsc_gpio_write()`, and `nsc_gpio_dump()` are shared helpers used by chip drivers.

Control flow: a chip driver fills `nsc_gpio_ops` with low-level accessors and exposes GPIOs through common file operations. User reads/writes go through `nsc_gpio_read()` / `nsc_gpio_write()`, which call the ops for the selected minor/pin. Dump support routes diagnostic output through the controller implementation.

State and persistence: this header owns no state. Runtime state is hardware register state plus driver private data behind the callback table. GPIO pin configuration persists only as hardware/platform state.

Dependencies and integration points: relies on `struct file`, user pointers, `struct module`, `struct device`, and U32 integer types from includers. It integrates legacy character-device style GPIO access with NSC/AMD/Winbond platform drivers.

Risks and test signals: risks include missing module ownership, invalid minor-to-pin mapping, user buffer handling bugs in shared file operations, and divergent semantics between Geode and PC-8736x callbacks. Test signals include read/write/change paths for each chip family, invalid minor tests, module unload while fds are open, and register dump validation on known hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nsc_gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nsfs.h -->
# sources/distributed-fs/ceph-client/include/linux/nsfs.h

Purpose: declares the namespace filesystem helper API for obtaining namespace paths/names, matching namespace device/inode pairs, and managing active namespace references held by nsproxies.

Important APIs/types/functions: `ns_get_path()`, `ns_get_path_cb()`, `ns_match()`, `ns_get_name()`, and `nsfs_init()` implement nsfs lookup and naming. `__current_namespace_from_type()` and `current_in_namespace()` use `_Generic` to compare concrete namespace pointers against current task namespace state. `nsproxy_ns_active_get()` and `nsproxy_ns_active_put()` adjust active references for every namespace in an nsproxy.

Control flow: procfs and callers ask nsfs for a `struct path` to a task namespace or to a namespace returned by a callback. Matching compares `dev_t`/inode pairs for namespace file handles. Current-namespace checks map a concrete namespace type to `current->nsproxy`, `task_active_pid_ns(current)`, or `current_user_ns()`.

State and persistence: nsfs keeps namespace dentries and active references while files, bind mounts, or nsproxies pin namespaces. The header itself stores no state but exposes operations that affect namespace visibility.

Dependencies and integration points: depends on `ns_common.h`, credentials, PID namespaces, task structs, paths, proc namespace operations, and current task macros. It integrates `/proc/<pid>/ns`, namespace file descriptors, VFS path handling, and namespace active-reference accounting.

Risks and test signals: risks include stale task namespace pointers, mishandled callback references in `ns_get_path_cb()`, namespace dev/inode collisions after recycling, and missing active ref drops during nsproxy teardown. Test signals include proc namespace symlink/open tests, bind-mounted namespace lifetime tests, `current_in_namespace()` compile coverage for every namespace type, and nsproxy active ref leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nsfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nsproxy.h -->
# sources/distributed-fs/ceph-client/include/linux/nsproxy.h

Purpose: defines `struct nsproxy`, the per-task bundle of namespace pointers shared by tasks that share all namespaces, plus APIs for copying, switching, unsharing, and exiting namespace sets.

Important APIs/types/functions: `struct nsproxy` holds refs to UTS, IPC, mount, PID-for-children, net, time, time-for-children, and cgroup namespaces. `struct nsset` carries a partial or complete install set plus flags, fs, and credentials. APIs include `copy_namespaces()`, `switch_cred_namespaces()`, `exit_nsproxy_namespaces()`, `get_cred_namespaces()`, `exit_cred_namespaces()`, `switch_task_namespaces()`, `exec_task_namespaces()`, `deactivate_nsproxy()`, `unshare_nsproxy_namespaces()`, and `nsproxy_cache_init()`. `get_nsproxy()` and `put_nsproxy()` manage the nsproxy refcount.

Control flow: fork/clone uses `copy_namespaces()` to share or duplicate namespace sets based on clone flags. unshare/setns paths build an `nsset` and install it into the current task. Exit paths drop task and credential namespace references. `put_nsproxy()` calls `deactivate_nsproxy()` when the last task reference disappears.

State and persistence: nsproxy state is task-lifetime in-memory state. The nsproxy refcount counts tasks sharing the bundle, while individual namespace lifetimes are tracked separately through namespace refs and active refs.

Dependencies and integration points: depends on refcounts, spinlocks, task locking rules, scheduler types, credentials, fs structs, and each namespace subsystem. It is the core bridge between process lifecycle, clone/unshare/setns/exec, and namespace reference management.

Risks and test signals: risks include changing another task's nsproxy without `task_lock`, confusing `pid_ns_for_children` with active PID namespace, credential namespace ref mismatches, and leaks during partial namespace install failures. Test signals include clone/unshare/setns regression tests, concurrent `/proc/<pid>/ns` access during exit, credential switch tests, and refcount debug coverage for shared nsproxy groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nsproxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nstree.h -->
# sources/distributed-fs/ceph-client/include/linux/nstree.h

Purpose: declares namespace tree roots and operations for ID generation, insertion, removal, lookup, and adjacent iteration across namespace types.

Important APIs/types/functions: global roots include `cgroup_ns_tree`, `ipc_ns_tree`, `mnt_ns_tree`, `net_ns_tree`, `pid_ns_tree`, `time_ns_tree`, `user_ns_tree`, and `uts_ns_tree`. Node/root helpers initialize and modify tree entries. `to_ns_tree()` maps concrete namespace pointers to the correct root. `ns_tree_gen_id()`, `ns_tree_add_raw()`, `ns_tree_add()`, `ns_tree_remove()`, `ns_tree_lookup_rcu()`, `ns_tree_adjoined_rcu()`, and `ns_tree_active()` expose tree behavior.

Control flow: namespace creation assigns or preserves an ID, inserts nodes into the per-type tree, and later removes them during teardown. RCU lookup and adjacent traversal support namespace discovery/listing without taking heavy locks in readers.

State and persistence: tree roots hold in-memory namespace indexes sorted by ID/type. IDs are runtime identifiers with special initial namespace IDs; they are not stable persistence across boot.

Dependencies and integration points: depends on namespace tree types, nsproxy definitions, rbtree, seqlock, RCU lists, cookie helpers, and nsfs UAPI constants. It integrates namespace lifetime management with listns/open-by-handle style discovery.

Risks and test signals: risks include RCU lookup use without active/main refs, duplicate ID insertion, removing inactive nodes twice, and `_Generic` tree mapping omissions. Test signals include namespace list ordering checks, concurrent creation/destruction lookup stress, init namespace ID preservation, and debug validation of `ns_tree_active()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nstree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ntb.h -->
# sources/distributed-fs/ceph-client/include/linux/ntb.h

Purpose: defines the generic Non-Transparent Bridge bus API used by NTB hardware drivers and client drivers to exchange link, memory-window, doorbell, scratchpad, message, DMA-device, and optional MSI capabilities.

Important APIs/types/functions: enums describe topology, link speed, link width, and default port roles. `struct ntb_client_ops`, `ntb_ctx_ops`, and `ntb_dev_ops` define client, callback, and hardware operation contracts. `struct ntb_client` and `struct ntb_dev` integrate with the device model. Public APIs register clients/devices, set/clear client context, publish link/doorbell/message events, query ports and resources, enable/disable links, configure inbound/outbound memory windows, access local and peer doorbells, scratchpads, and messages, select DMA devices, compute multiport resource indexes, and use optional `CONFIG_NTB_MSI` descriptors and IRQ helpers.

Control flow: a hardware driver fills `ntb_dev_ops` and calls `ntb_register_device()`. A client registers with `ntb_register_client()`, probes an accepted NTB, installs context callbacks with `ntb_set_ctx()`, enables the link, configures memory windows, and uses doorbells/messages/scratchpads for synchronization. Hardware interrupt handlers call `ntb_link_event()`, `ntb_db_event()`, or `ntb_msg_event()` to notify the client under context locking.

State and persistence: `struct ntb_dev` stores topology, PCI device, ops, client context, context ops, context spinlock, release completion, and optional MSI state. Hardware registers hold link/window/doorbell/scratchpad state; no durable software state is stored by the header.

Dependencies and integration points: depends on device model, PCI, interrupt handlers, completions, DMA/phys/resource types, modules, and optional NTB MSI support. It integrates NTB core, vendor hardware drivers, NTB transport, DMA engines, and client protocols.

Risks and test signals: risks include incomplete `ntb_dev_ops` tables, optional callback fallback returning success when no translation is done, peer/local doorbell callback checks that can mask missing peer ops, multiport resource-index mistakes, link-state races before memory-window setup, and MSI unsupported paths. Test signals include ntb_tool/ntb_perf, two-port and multiport topology tests, doorbell vector masking tests, memory-window alignment/clear tests, link flap stress, DMA peer doorbell address tests, and builds with and without `CONFIG_NTB_MSI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ntb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ntb_transport.h -->
# sources/distributed-fs/ceph-client/include/linux/ntb_transport.h

Purpose: declares the higher-level NTB transport client API that builds queue pairs over NTB memory windows and doorbells.

Important APIs/types/functions: `struct ntb_transport_client` supplies probe/remove callbacks for transport devices. `ntb_transport_register_client()`, `ntb_transport_unregister_client()`, `ntb_transport_register_client_dev()`, and `ntb_transport_unregister_client_dev()` manage clients and named devices. `struct ntb_queue_handlers` supplies receive, transmit, event, and error callbacks. Queue APIs create/free queue pairs, enqueue RX/TX buffers, remove RX buffers, bring links up/down, and query link state.

Control flow: a transport client registers, receives a queue-pair device in probe, allocates a queue with handlers, posts receive buffers, enqueues transmit buffers, and reacts to link/event/error callbacks. Link helpers expose per-queue state independently of raw NTB link state.

State and persistence: queue-pair state lives in the transport implementation: posted buffers, callbacks, link state, and NTB resources. This header stores only opaque handles and callback contracts.

Dependencies and integration points: depends on NTB core, `struct device`, and transport implementation. It integrates raw NTB resources with client protocols that want message queues rather than direct doorbell/window management.

Risks and test signals: risks include buffer ownership ambiguity after enqueue/remove, callbacks racing with queue free, link state mismatch between NTB and transport, and missing RX buffers causing dropped traffic. Test signals include ntb_netdev/ntb_pingpong style traffic, queue teardown during link down, callback ordering tests, and buffer leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ntb_transport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nubus.h -->
# sources/distributed-fs/ceph-client/include/linux/nubus.h

Purpose: declares the classic Macintosh NuBus resource, board, driver, procfs, and device-model interfaces.

Important APIs/types/functions: `struct nubus_dir`, `nubus_dirent`, `nubus_board`, and `nubus_rsrc` model ROM directories, resources, boards, slots, categories, types, and driver data. `struct nubus_driver` provides match/probe/remove. Iteration macros walk global and per-board resources. Directory APIs get root/board/function directories, read or find resources, rewind, get subdirectories, copy resource memory, and emit seq_file output. Device/driver APIs register NuBus devices and drivers and provide drvdata helpers. `nubus_slot_addr()` maps slot numbers to physical slot address space.

Control flow: platform NuBus discovery populates boards and function resources, optional procfs exposes resource data, drivers register a `nubus_driver`, match resources, probe boards, and store private data on the board device.

State and persistence: state is boot/discovery-time hardware inventory in lists and device model objects. Resource ROM data is hardware-provided and read-only; procfs entries are derived views.

Dependencies and integration points: depends on device model, list heads, procfs, seq_file, and architecture slot address mapping. It integrates m68k Macintosh bus discovery, legacy drivers, and optional procfs diagnostics.

Risks and test signals: risks include malformed ROM directory parsing, bad slot address calculations, driver/resource lifetime mismatches, and procfs stubs hiding missing diagnostics. Test signals include NuBus enumeration on supported m68k configs, resource iterator coverage, procfs dump validation, driver register/unregister tests, and invalid directory entry fuzzing where feasible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nubus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/numa.h -->
# sources/distributed-fs/ceph-client/include/linux/numa.h

Purpose: provides generic NUMA node helper declarations and config-dependent fallbacks for node validity, node-data allocation, nearest-node lookup, memory hotplug node mapping, and memblock filling.

Important APIs/types/functions: `NUMA_NO_MEMBLK`, `numa_valid_node()`, `NODE_DATA()`, `alloc_node_data()`, `alloc_offline_node_data()`, `numa_nearest_node()`, `nearest_node_nodemask()`, `memory_add_physaddr_to_nid()`, `phys_to_target_node()`, `numa_fill_memblks()`, and `numa_map_to_online_node()` are the main interfaces. `__initdata_or_meminfo` changes section placement depending on `CONFIG_NUMA_KEEP_MEMINFO`.

Control flow: early architecture NUMA parsing allocates per-node `pglist_data`, maps memory ranges to nodes, and later memory hotplug asks for the node that should own a physical address. Non-NUMA builds collapse most helpers to node 0 or `NUMA_NO_NODE`.

State and persistence: state is boot-time NUMA topology and per-node memory data in `node_data[]`. It persists for kernel runtime and changes only through memory hotplug or architecture-specific updates.

Dependencies and integration points: depends on node masks, memblock/init attributes, `MAX_NUMNODES`, and memory hotplug. It integrates architecture NUMA discovery, MM initialization, sysfs node attributes, and hotplug node selection.

Risks and test signals: risks include invalid node IDs, non-NUMA fallback mismatches, wrong physical-address-to-node mapping for hotplug, and initdata lifetime issues when meminfo is kept. Test signals include NUMA boot on multi-node systems, memory hotplug tests, nearest-node behavior with offline nodes, and compile coverage with `CONFIG_NUMA` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/numa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/numa_memblks.h -->
# sources/distributed-fs/ceph-client/include/linux/numa_memblks.h

Purpose: declares early NUMA memory-block tracking and optional NUMA emulation interfaces used while converting firmware memory ranges into node topology.

Important APIs/types/functions: `NR_NODE_MEMBLKS`, `struct numa_memblk`, and `struct numa_meminfo` model start/end/node memory ranges. APIs set/reset node distances, add normal and reserved memblocks, remove memblocks, clean/merge meminfo, initialize NUMA memblocks through an architecture callback, and expose `numa_distance_cnt`. Under `CONFIG_NUMA_EMU`, emulation APIs parse command-line input, map emulated to physical nodes, compute DMA end, and rewrite CPU/node and meminfo mappings.

Control flow: architecture setup adds firmware memory ranges with node IDs, cleans the meminfo table, sets distance information, optionally rewrites topology for NUMA emulation, and then MM initialization consumes the ranges for node data and zones.

State and persistence: memblock lists are early-boot topology state and may be retained when `CONFIG_NUMA_KEEP_MEMINFO` is enabled. Emulation maps persist for runtime node interpretation.

Dependencies and integration points: depends on `linux/numa.h`, `MAX_NUMNODES`, init annotations, and architecture callbacks. It integrates firmware NUMA parsing, reserved memory tracking, distance matrices, memory hotplug node lookup, and NUMA emulation.

Risks and test signals: risks include overlapping/unsorted ranges, exceeding `NR_NODE_MEMBLKS`, distance matrix leaks/stale values, emulated-to-physical node confusion, and incorrect reserved-range handling. Test signals include ACPI/SRAT or device-tree NUMA boot, fake NUMA command-line tests, memblock overlap cleanup tests, node distance sysfs validation, and hotplug physical address mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/numa_memblks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-auth.h -->
# sources/distributed-fs/ceph-client/include/linux/nvme-auth.h

Purpose: declares NVMe DH-HMAC-CHAP authentication and TLS PSK derivation helpers used by NVMe fabrics host and target code.

Important APIs/types/functions: `struct nvme_dhchap_key` stores a counted key plus hash ID. Mapping helpers convert DH group and HMAC IDs to names, crypto KPP names, lengths, and IDs. `struct nvme_auth_hmac_ctx` wraps SHA-256/SHA-384/SHA-512 HMAC contexts. APIs initialize/update/finalize HMACs, allocate/extract/parse/free/transform keys, compute augmented challenges, generate DH private/public/session keys, generate PSKs, generate digest strings, and derive TLS PSKs.

Control flow: authentication negotiation selects a hash and DH group, parses host/subsystem secrets, optionally transforms them by NQN, generates challenges and DH material, derives a session key/PSK, and finally produces digests or TLS PSKs for fabrics security.

State and persistence: key objects and HMAC/DH contexts are in-memory sensitive material. Persistent secrets live outside this header in configuration or keyrings; callers must free and avoid leaking derived material.

Dependencies and integration points: depends on kernel crypto KPP and SHA2 HMAC implementations plus NVMe auth constants in `nvme.h`. It integrates NVMe fabrics authentication, NVMe keyring/TLS setup, and host/subsystem NQN identity.

Risks and test signals: risks include unsupported hash/group negotiation, incorrect key parsing or NQN transformation, insufficient zeroization in implementation, challenge concatenation mismatch, and digest/PSK length errors. Test signals include DH-HMAC-CHAP positive/negative handshake tests, invalid secret parsing, all hash/group combinations, TLS PSK derivation vectors, and memory-sanitizer checks for freed key paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-fc-driver.h -->
# sources/distributed-fs/ceph-client/include/linux/nvme-fc-driver.h

Purpose: defines the low-level driver API between Fibre Channel LLDDs and the NVMe-FC host and target transports.

Important APIs/types/functions: common LS structures `nvmefc_ls_req` and `nvmefc_ls_rsp` describe DMA buffers, timeouts, private areas, and completion callbacks. Host-side types include `nvme_fc_port_info`, `nvmefc_fcp_req`, `nvme_fc_local_port`, `nvme_fc_remote_port`, and `nvme_fc_port_template`; APIs register/unregister local and remote ports, rescan remote ports, set dev-loss timeout, receive LS requests, and obtain request UUID/appid. Target-side types include `nvmet_fc_port_info`, `nvmefc_tgt_fcp_req`, `nvmet_fc_target_port`, and `nvmet_fc_target_template`; APIs register/unregister target ports, receive LS and FCP requests, invalidate hosts, and report FCP aborts.

Control flow: an LLDD registers a local host port or target port with a template of mandatory callbacks. Host transport issues LS requests and FCP I/O through LLDD callbacks, and the LLDD completes via provided `done` callbacks. Target transport accepts received LS/FCP requests from the LLDD, then calls back into the LLDD to transmit LS responses, perform read/write data movement, send responses, abort commands, and release exchange contexts.

State and persistence: port objects store static WWNN/WWPN/role numbers, dynamic port IDs/states, dev-loss timeout, and LLDD private memory allocated alongside transport objects. Request structures hold transient DMA/exchange state until completion/release.

Dependencies and integration points: depends on scatterlists, blk-mq queue maps, DMA addresses, FC BA_RJT definitions, device model, and NVMe-FC protocol structures. It integrates SCSI/FC LLDDs, NVMe host transport, NVMe target transport, block queue mapping, dev-loss recovery, discovery, and appid/UUID tagging.

Risks and test signals: risks include failing mandatory callbacks, calling `done` twice or never, using request/exchange structures after transport release, unregister races with pending LS responses, wrong transferred-length/fcp-error reporting, queue affinity mismatches, and hosthandle lifetime mistakes after invalidation. Test signals include host login/create association/create queue flows, target read/write/response flows, LS abort and FCP abort tests, remote-port dev-loss/reconnect tests, unregister with outstanding exchanges, queue mapping tests, and FC-NVMe interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-fc-driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-fc.h -->
# sources/distributed-fs/ceph-client/include/linux/nvme-fc.h

Purpose: defines FC-NVMe wire-format constants and structures for command IUs, response IUs, status/readiness IUs, link-service descriptors, link-service payloads, timeouts, and transport address formatting.

Important APIs/types/functions: command flags encode read/write and protection information. `fccmnd_set_cat_admin()` and `fccmnd_set_cat_css()` set command category bits. `struct nvme_fc_cmd_iu`, `nvme_fc_ersp_iu`, `nvme_fc_nvme_sr_iu`, and `nvme_fc_nvme_sr_rsp_iu` model FCP command/response/readiness exchanges. Link-service enums and descriptors model create association, create connection, disconnect association/connection, accept, reject, association ID, and connection ID. TRADDR macros define FC address string lengths and offsets.

Control flow: host and target code build link-service requests to create associations/connections, accept or reject them using descriptor lists, exchange NVMe command IUs and response IUs over FC sequences, and use disconnect LS payloads for teardown. Helpers fill length/category fields according to FC-NVMe layout rules.

State and persistence: no software state is owned here. Structures represent on-wire transient protocol payloads; association and connection IDs persist only for the lifetime of the FC-NVMe session.

Dependencies and integration points: depends on FC UAPI constants from `fc_fs.h`, NVMe command/completion structures, endian types, UUIDs, and offset calculations. It integrates `nvme-fc-driver.h`, NVMe host/target transports, and FC LLDD payload parsing.

Risks and test signals: risks include endian mistakes, descriptor length miscalculation, accepting malformed descriptor lists, TRADDR parsing inconsistencies with required `0x` prefixes, and mismatched association/connection IDs. Test signals include protocol conformance tests for LS payload sizes, create/disconnect association flows, invalid reject reason/explanation handling, FC-NVMe interop, and fuzzing of LS descriptor lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-keyring.h -->
# sources/distributed-fs/ceph-client/include/linux/nvme-keyring.h

Purpose: declares NVMe TLS PSK keyring integration for storing, refreshing, selecting, and looking up keys used by secure NVMe/TCP or fabrics connections.

Important APIs/types/functions: when `CONFIG_NVME_KEYRING` is enabled, `nvme_tls_psk_refresh()` creates or updates a PSK entry for host NQN, subsystem NQN, HMAC ID, key data, and digest; `nvme_tls_psk_default()` finds a default key serial; `nvme_keyring_id()` returns the NVMe keyring serial; and `nvme_tls_key_lookup()` resolves a serial to a key. Disabled builds return `-ENOTSUPP` or zero.

Control flow: authentication or connection setup derives/obtains key material, refreshes the keyring entry, then stores or passes key serials to TLS setup. Lookup converts a configured serial into a live `struct key`.

State and persistence: key material lives in the kernel key retention service and follows keyring lifetime/permissions. This header owns no state but gates whether callers can use keyring-backed PSKs.

Dependencies and integration points: depends on `linux/key.h`, key serial types, errno pointers, NVMe authentication helpers, and kernel TLS consumers. It integrates NVMe DH-HMAC-CHAP PSK derivation with Linux keyrings.

Risks and test signals: risks include disabled-config fallback handling, key permission/ownership failures, stale digest-to-key mapping, serial reuse, and leaking PSK material. Test signals include keyring-enabled and disabled builds, PSK refresh/default lookup tests, permission-negative tests, TLS connection setup using selected keys, and key lifetime cleanup checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-keyring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-rdma.h -->
# sources/distributed-fs/ceph-client/include/linux/nvme-rdma.h

Purpose: defines NVMe/RDMA private connection-management data formats, default ports, queue-size limits, status codes, and status text helpers.

Important APIs/types/functions: constants include `NVME_RDMA_IP_PORT`, maximum/default queue sizes, and metadata queue limits. `enum nvme_rdma_cm_fmt` identifies private data format 1.0. `enum nvme_rdma_cm_status` lists rejection reasons. `nvme_rdma_cm_msg()` maps rejection codes to strings. `struct nvme_rdma_cm_req`, `nvme_rdma_cm_rep`, and `nvme_rdma_cm_rej` define little-endian RDMA CM request, reply, and reject private data payloads.

Control flow: RDMA connection setup sends a request containing queue ID, host receive/send queue sizes, and controller ID; the controller replies with controller receive queue size or rejects with a status. Host and target code use the helper string for diagnostics.

State and persistence: no state is stored. Structures are transient RDMA CM private data exchanged during queue connection.

Dependencies and integration points: depends on fixed-width endian types and RDMA CM users in the NVMe/RDMA transport. It integrates fabrics queue setup with RDMA connection negotiation.

Risks and test signals: risks include endian mistakes, accepting invalid qid/queue sizes, mismatch between metadata and normal queue limits, and missing diagnostics for new status codes. Test signals include NVMe/RDMA connect/reject tests, invalid private-data length tests, queue-size boundary tests, and interop with target implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-tcp.h -->
# sources/distributed-fs/ceph-client/include/linux/nvme-tcp.h

Purpose: defines NVMe/TCP PDU wire formats, protocol constants, digest/TLS options, fatal error codes, and a union over all supported PDU layouts.

Important APIs/types/functions: constants include discovery port 8009, admin capsule size, digest length, and termination PDU size limits. Enums define protocol format version, TLS cipher IDs, fatal error status values, digest option bits, PDU types, and PDU flags. `struct nvme_tcp_hdr` is the common PDU header. Specific structures model ICReq, ICResp, termination, command capsule, response capsule, R2T, and data PDUs; `union nvme_tcp_pdu` overlays them.

Control flow: a TCP queue starts with ICReq/ICResp negotiation of version, alignment, digests, and R2T/data limits. Command PDUs carry NVMe commands, responses carry completions, R2T PDUs authorize host-to-controller data, data PDUs transfer payload, and termination PDUs report fatal protocol errors.

State and persistence: no state is stored by the header. The structures describe transient socket payloads; connection state lives in the NVMe/TCP host/target implementations.

Dependencies and integration points: depends on `linux/nvme.h` for command/completion structures and size macros. It integrates NVMe fabrics core, TCP transport parsing, optional header/data digests, and TLS cipher negotiation.

Risks and test signals: risks include PDU length/data-offset validation bugs, digest flag mismatch, duplicate fatal error code values, alignment negotiation mistakes, R2T/data limit enforcement, and TLS cipher mapping errors. Test signals include NVMe/TCP connect tests with/without digests and TLS, malformed PDU fuzzing, R2T boundary tests, termination PDU validation, and interop with target stacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme.h -->
# sources/distributed-fs/ceph-client/include/linux/nvme.h

Purpose: provides the core NVMe specification vocabulary for kernel code: register offsets, bit fields, identify/log data structures, admin/I/O/fabrics commands, authentication payloads, completion/status definitions, and helper macros.

Important APIs/types/functions: constants define NQN/address sizes, discovery subsystem name, queue depths, register offsets, controller capabilities, CC/CSTS bits, CMB/PMR fields, feature/log IDs, status codes, and version helpers. Structures model identify controller/namespace data, ZNS/NVM command-set data, SMART/FW/effects/ANA/zone/FDP/reservation logs, SGL/PRP data pointers, all major I/O/admin/fabrics command layouts, discovery log entries, DH-HMAC-CHAP auth messages, completion entries, and persistent reservation payloads. Helpers include LBA format extraction, command opcode symbolic formatting, `nvme_is_fabrics()`, `nvme_is_write()`, verbose opcode/status string fallbacks, and version field extraction.

Control flow: host, target, and transport code fill `struct nvme_command` unions for admin, I/O, or fabrics operations; controllers return `struct nvme_completion`; identify/log commands transfer fixed 4096-byte or variable payloads; fabrics connect/auth/property commands use the same capsule model over RDMA/TCP/FC. Helpers classify command type and choose diagnostic strings.

State and persistence: this header stores no runtime state. Many structures describe persistent device data or controller state as reported by hardware, while command/completion structures are transient wire/MMIO/queue entries.

Dependencies and integration points: depends on bit helpers, fixed-width types, UUIDs, trace-print symbolic macros from includers, and transport headers. It is the central integration contract for NVMe PCI, fabrics, target, multipath/ANA, reservations, authentication, ZNS, FDP, and block-layer code.

Risks and test signals: risks include spec drift, wrong endian annotations, structure size/layout regressions, conflicting command/status values across command sets, variable-length array bounds, and helper classification mistakes for fabrics write direction. Test signals include static asserts for 4096-byte identify structures, nvme-cli identify/log comparisons, tracepoint opcode/status decoding, fabrics connect/auth tests, ZNS/FDP/reservation command tests, and ABI/layout compile checks across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvmem-consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/nvmem-consumer.h

Purpose: declares the NVMEM consumer API for drivers that read or write named cells or raw offsets from EEPROM/OTP/FRAM/battery-backed memory providers.

Important APIs/types/functions: `struct nvmem_cell_lookup` maps provider name, cell name, consumer device ID, and connection ID. Notifier events cover provider, cell, and layout add/remove. Cell APIs get/put cells, read/write cell buffers, and read typed fixed or variable little-endian integers. Device APIs get/put NVMEM devices, read/write raw offsets, read/write cells by `nvmem_cell_info`, query name/size, add/remove lookup tables, register notifiers, and find devices. OF helpers get cells/devices by device node. Disabled builds return `-EOPNOTSUPP`, `ERR_PTR()`, zero, or NULL stubs.

Control flow: a consumer driver obtains a cell or provider by device and name, reads or writes data, and releases it manually or through devm. Platform lookup entries or device tree map consumer names to provider cells. Notifiers let interested code react to provider/cell/layout registration changes.

State and persistence: NVMEM data may be persistent hardware storage. Consumer handles are kernel references to provider devices/cells; lookup tables and notifier registrations are in-memory configuration state.

Dependencies and integration points: depends on errno/ERR_PTR helpers, notifier chains, device and device-tree types, and provider cell metadata. It integrates board data, OF bindings, driver probe code, and NVMEM provider implementations.

Risks and test signals: risks include assuming NVMEM exists when config stubs return unsupported, endian/variable-length misreads, writing read-only OTP cells, leaking cell/device references, and notifier unregister races. Test signals include provider/consumer probe ordering tests, OF and lookup-table resolution, typed read helpers with short/long cells, disabled-config builds, and read-only/write-failure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvmem-consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvmem-provider.h -->
# sources/distributed-fs/ceph-client/include/linux/nvmem-provider.h

Purpose: declares the NVMEM provider and layout-driver API used by hardware drivers to export non-volatile memory regions and by layout parsers to add derived cells.

Important APIs/types/functions: callback typedefs define raw register read/write and cell post-processing. `enum nvmem_type` classifies EEPROM, OTP, battery-backed, and FRAM storage. `struct nvmem_keepout` marks forbidden ranges. `struct nvmem_cell_info` describes named cells, bit slicing, raw/cooked lengths, OF nodes, and optional read post-processing. `struct nvmem_config` describes provider registration: parent, name/id, owner, predefined cells, legacy OF cell parsing, DT fixups, keepouts, type, read-only/root-only/write-protect behavior, layout, callbacks, size, word size, stride, private data, and legacy compatibility. `struct nvmem_layout` and `nvmem_layout_driver` define dynamic parsers. APIs register/unregister providers and layouts, add cells, and provide devm/module helpers.

Control flow: a hardware provider fills `nvmem_config` with access callbacks and metadata, then registers an `nvmem_device`. The core validates stride/word size, exposes cells, applies keepouts and post-processing, and notifies consumers. Layout drivers can probe attached layouts and add parsed cells at runtime.

State and persistence: provider state includes registered device objects, cell tables, lookup metadata, layout devices, and hardware-backed non-volatile content. Actual persistence depends on the storage type and provider callbacks.

Dependencies and integration points: depends on device model, driver core, GPIO write-protect control, OF layout containers, modules, and NVMEM consumer metadata. It integrates EEPROM/OTP/SoC fuse drivers, device tree bindings, and consumers needing calibration/MAC/key data.

Risks and test signals: risks include incorrect size/stride/word-size validation, keepout ranges not sorted or enforced, bit-cell extraction mistakes, write-protect handling, post-processing changing expected lengths, and layout-added cell lifetime issues. Test signals include provider registration tests, raw and cell read/write boundary tests, keepout fill-value checks, read-only/root-only permission checks, OF layout parsing, and disabled-config compile stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvmem-provider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvram.h -->
# sources/distributed-fs/ceph-client/include/linux/nvram.h

Purpose: defines a portable NVRAM operation table and wrapper helpers for architecture NVRAM access.

Important APIs/types/functions: `struct nvram_ops` may provide size, byte read/write, range read/write, and x86/m68k initialize/checksum operations. `arch_nvram_ops` is the generic architecture implementation. Inline wrappers `nvram_get_size()`, `nvram_read_byte()`, `nvram_write_byte()`, `nvram_read_bytes()`, `nvram_write_bytes()`, `nvram_read()`, and `nvram_write()` choose PPC machdep hooks when `CONFIG_PPC` is set, otherwise use `arch_nvram_ops`, falling back from range operations to byte loops.

Control flow: callers use generic wrappers. The wrappers check for architecture-provided optimized operations, fall back to byte access, update file offsets while reading/writing, and stop at reported NVRAM size.

State and persistence: NVRAM content is persistent platform storage. The header owns no state, but writes may update hardware and checksums through architecture callbacks.

Dependencies and integration points: depends on errno, UAPI NVRAM definitions, PPC `ppc_md` hooks, and architecture-specific `arch_nvram_ops`. It integrates legacy `/dev/nvram`, platform firmware variables, and architecture NVRAM backends.

Risks and test signals: risks include no size provider returning `-ENODEV`, byte fallback ignoring checksum semantics, offset truncation at device end, PPC/generic behavior divergence, and writes without checksum updates when only byte hooks exist. Test signals include read/write boundary tests, missing backend tests, checksum validation on x86/m68k, PPC machdep hook coverage, and persistence checks across reboot where hardware permits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/oa_tc6.h -->
# sources/distributed-fs/ceph-client/include/linux/oa_tc6.h

Purpose: declares the OPEN Alliance 10BASE-T1x MAC-PHY Serial Interface framework used by SPI-connected Ethernet MAC-PHY devices.

Important APIs/types/functions: `struct oa_tc6` is opaque framework state. `oa_tc6_init()` binds an SPI device and net device, `oa_tc6_exit()` tears it down, register helpers read/write one or multiple 32-bit registers, `oa_tc6_start_xmit()` transmits an skb through the TC6 data path, and `oa_tc6_zero_align_receive_frame_enable()` enables zero-alignment receive-frame behavior.

Control flow: an Ethernet MAC-PHY driver initializes TC6 with its SPI and netdev objects, uses register helpers for device setup, routes netdev transmit through `oa_tc6_start_xmit()`, enables optional receive alignment behavior, and calls exit during remove.

State and persistence: framework state is runtime SPI/netdev coordination state; hardware register values persist only according to device reset/power behavior. Packet buffers are transient.

Dependencies and integration points: depends on Ethernet netdev/skb types and SPI device APIs. It integrates SPI MAC-PHY drivers with the networking stack and OPEN Alliance TC6 register/data protocol implementation.

Risks and test signals: risks include SPI transfer framing errors, register burst length mistakes, netdev lifetime races, skb ownership errors, and receive alignment mismatches. Test signals include link bring-up on TC6 hardware, register read/write round trips, TX/RX packet tests, remove while traffic is active, and error injection for SPI failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/oa_tc6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objagg.h -->
# sources/distributed-fs/ceph-client/include/linux/objagg.h

Purpose: declares an object aggregation library that groups raw objects into roots plus deltas, useful when hardware tables can share common state and represent differences compactly.

Important APIs/types/functions: `struct objagg_ops` defines object size, delta feasibility, delta create/destroy, root create/destroy, and root ID handling. `objagg_create()` / `objagg_destroy()` manage an aggregator. `objagg_obj_get()` / `objagg_obj_put()` acquire/release aggregated objects. Accessors return root private data, delta private data, and raw object data. Stats structures report root count, user counts, delta user counts, and root/delta classification. Hint APIs compute and consume optimization hints using algorithms such as simple greedy.

Control flow: a client creates an aggregator with callbacks, submits raw objects, and the library either reuses an existing root/delta relation or creates a new root. Releasing objects drops users and destroys delta/root private data when unused. Hints can be generated from one run and used to improve a later aggregation plan.

State and persistence: aggregation state is in-memory: roots, deltas, user counts, raw object copies, stats, and hints. Hardware state may be programmed by callbacks but is owned by the client.

Dependencies and integration points: depends on client callback semantics and unsigned root IDs. It integrates with networking/offload-style drivers that need compact shared hardware representations.

Risks and test signals: risks include callback-created hardware state leaking on partial failure, invalid delta equivalence, root ID exhaustion, stats lifetime misuse, and poor hints causing unexpected resource growth. Test signals include duplicate object get/put, delta/root destroy ordering, simulated callback failures, hint generation/application comparisons, and hardware table resource-limit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objagg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objpool.h -->
# sources/distributed-fs/ceph-client/include/linux/objpool.h

Purpose: defines a fixed-capacity, preallocated, lockless-ish per-CPU object pool optimized for contexts where allocation is prohibited or expensive, such as probes and interrupt/thread mixed consumers.

Important APIs/types/functions: `struct objpool_slot` is a per-CPU ring with `head`, `tail`, `last`, mask, and object entries. `struct objpool_head` stores object size/count, CPU count, per-slot capacity, GFP flags, refcount, flags, slot array, release callback, and caller context. `objpool_init()` allocates and initializes objects. `objpool_pop()` disables local IRQs and scans per-CPU slots for an object. `objpool_push()` returns an object to the current CPU slot. `objpool_drop()`, `objpool_free()`, and `objpool_fini()` handle asynchronous teardown. Internal helpers use acquire/release loads, stores, and cmpxchg on ring indexes.

Control flow: callers initialize a pool with a fixed number of objects and optional per-object init callback. Allocation pops from the local CPU slot first, then other possible CPUs. Reclamation pushes to the current CPU slot and publishes via `last`. Teardown releases unused objects and waits for outstanding objects to be dropped in asynchronous use cases.

State and persistence: all state is in-memory preallocated object and ring metadata. Capacity is fixed after initialization. The pool may outlive `objpool_fini()` until outstanding borrowed objects call `objpool_drop()`.

Dependencies and integration points: depends on refcounts, atomics, cpumasks, IRQ flag helpers, SMP CPU iteration, memory barriers, and GFP allocation. It integrates with kretprobe/rethook-style users that need safe object reuse from constrained contexts.

Risks and test signals: risks include double-push or wrong-object push corrupting rings, wraparound assumptions, insufficient barriers causing stale entries, teardown while `objpool_push()` is in flight, and memory overhead from per-CPU rings. Test signals include `test_objpool`, high-concurrency push/pop stress, IRQ/thread mixed use, CPU hotplug/possible CPU configurations, asynchronous outstanding-object teardown, and KCSAN/KASAN runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objpool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objtool.h -->
# sources/distributed-fs/ceph-client/include/linux/objtool.h

Purpose: provides C and assembly annotation macros consumed by objtool for unwind hinting, stack-frame validation exceptions, reachable-code marking, and mitigation validation markers.

Important APIs/types/functions: when `CONFIG_OBJTOOL` is enabled, `UNWIND_HINT()` emits records into `.discard.unwind_hints`; `STACK_FRAME_NON_STANDARD()` and `STACK_FRAME_NON_STANDARD_FP()` mark functions exempt from stack-frame validation; `ASM_REACHABLE` emits `.discard.reachable`; assembly variants define equivalent macros. Disabled builds make these annotations empty. `VALIDATE_UNRET_BEGIN` maps to `ANNOTATE_UNRET_BEGIN` only for configured noinstr validation and unret/SRSO mitigation combinations.

Control flow: low-level C inline asm or assembly entry code places hints at control-flow points. Objtool reads discard sections during build analysis, validates stack/unwind state, and generates ORC metadata or suppresses warnings for marked non-standard functions.

State and persistence: annotations are build-time metadata in special ELF sections, discarded or consumed during tooling. They affect generated unwind metadata, not runtime mutable state.

Dependencies and integration points: depends on `objtool_types.h`, annotation macros, config options for objtool/frame pointers/noinstr validation, and assembly preprocessing. It integrates architecture entry code, ORC unwinder generation, retpoline/unret validation, and kernel build checks.

Risks and test signals: risks include overusing non-standard frame exemptions, incorrect unwind hints causing bad stack traces, missing assembly annotations for entry/interrupt code, and config-dependent annotation drift. Test signals include objtool warning-free builds, ORC unwind selftests, frame-pointer builds, noinstr validation with mitigations enabled, and runtime stack traces through annotated assembly paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objtool_types.h -->
# sources/distributed-fs/ceph-client/include/linux/objtool_types.h

Purpose: defines the compact data structures and numeric constants shared by objtool annotations in C and assembly.

Important APIs/types/functions: `struct unwind_hint` stores instruction offset, stack pointer offset, stack register, hint type, and signal flag. `UNWIND_HINT_TYPE_*` constants classify undefined coverage, end-of-stack, call frames, full/partial pt_regs, function generation, and save/restore pseudo-hints. `ANNOTYPE_*` constants identify no-ENDBR, retpoline-safe, instrumentation begin/end, unret begin, ignore alternatives, intra-function call, reachable, and no-CFI annotations. `ANNOTYPE_DATA_SPECIAL` tags special annotation data.

Control flow: `objtool.h` macros encode these values into special sections. Objtool decodes them while walking instructions and validating unwind/control-flow metadata.

State and persistence: no runtime state is stored. The values are compile-time ABI between annotated kernel code and objtool.

Dependencies and integration points: depends on fixed-width Linux types for C builds and must also be parseable by assembly. It integrates annotation emitters, objtool, ORC unwinder metadata generation, and mitigation validators.

Risks and test signals: risks include changing numeric constants without updating objtool, structure layout mismatches between C and assembly emission, and missing hint types for new entry patterns. Test signals include objtool build coverage, section decoding tests, ORC unwind validation, and assembly/C annotation compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objtool_types.h -->
