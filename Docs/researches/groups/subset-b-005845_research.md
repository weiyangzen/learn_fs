# Research: subset-b-005845

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bnxt/ulp.h -->
# sources/distributed-fs/ceph-client/include/linux/bnxt/ulp.h

Purpose: Defines the Broadcom NetXtreme-C/E Ethernet driver interface used by upper-layer protocol devices, especially RoCE/RDMA and firmware-control auxiliary devices. It is a kernel-internal contract between the `bnxt` L2 driver, auxiliary bus children, firmware messaging, interrupt-vector allocation, and async firmware event delivery.

Important APIs/types/functions: `enum bnxt_auxdev_type` identifies RDMA and firmware-control auxiliary devices. `struct bnxt_aux_priv` embeds `struct auxiliary_device` and links it back to `struct bnxt_en_dev`. `struct bnxt_msix_entry` describes allocated vectors, completion ring index, and doorbell offset. `struct bnxt_ulp_ops` is the callback vtable for upper-layer async events and IRQ stop/restart. `struct bnxt_fw_msg` carries HWRM request/response buffers and timeout. `struct bnxt_ulp` stores the upper-layer handle, RCU-protected ops pointer, async event bitmap, and requested MSI-X count. `struct bnxt_en_dev` exposes NIC, PCI, doorbell, chip, stats, state, BAR, and ULP resource accounting fields plus an operation mutex. Externs cover MSI-X/stat context getters/setters, ULP start/stop, IRQ restart, SR-IOV changes, auxiliary-device lifecycle, ULP registration, firmware message send, async-event registration, and auxiliary ID allocation.

Control flow: The L2 driver initializes auxiliary devices, exports an `bnxt_en_dev`, and an upper-layer driver registers callbacks via `bnxt_register_dev()`. Runtime paths check `bnxt_ulp_registered()` with `rcu_access_pointer()`, dispatch firmware async completions through `ulp_async_notifier()` in bottom-half context, and coordinate IRQ quiesce/restart around reset or error recovery. Firmware requests flow through `bnxt_send_msg()`.

State/persistence: State is volatile kernel driver state: registered ops, async event bitmap, MSI-X/stat context reservations, doorbell geometry, flags such as RoCE capability, VF, stopped, and software resource limits. `en_dev_lock` serializes ULP operations, while callback lookup uses RCU.

Dependencies/integration: Depends on auxiliary bus, PCI/net device context, HWRM completion structs, and the core `bnxt` driver implementation. Integrates with RDMA/RoCE auxiliary drivers and firmware-control clients.

Risks/test signals: High-risk areas are RCU callback lifetime, non-sleeping async notifier context, interrupt vector accounting across PF/VF/SR-IOV, and doorbell offset correctness. Test signals include RDMA auxiliary probe/remove, RoCE traffic through reset, firmware async-event delivery, SR-IOV VF count changes, MSI-X exhaustion, and unload/reload with KASAN/lockdep/RCU diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bnxt/ulp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bootconfig.h -->
# sources/distributed-fs/ceph-client/include/linux/bootconfig.h

Purpose: Declares the Extra Boot Config parser interface and compact tree representation used during early boot, plus a limited userspace-compatible surface for `tools/bootconfig` sanity tests. It defines how bootconfig data embedded in initrd or kernel image is identified, checksummed, parsed, traversed, and released.

Important APIs/types/functions: Constants define the `#BOOTCONFIG\n` magic, 4-byte alignment, maximum data size, node count, key length, and nesting depth. `xbc_calc_checksum()` performs the additive checksum used with size and magic when appending bootconfig to initrd. `struct xbc_node` is a packed 16-bit index node with `next`, `child`, `parent`, and tagged `data` fields; `XBC_VALUE` distinguishes value nodes from key nodes. Raw accessors include `xbc_root_node()`, node index/parent/child/next/data getters. Tree APIs include `xbc_node_find_subkey()`, `xbc_node_find_value()`, leaf/key-value iteration helpers, and `xbc_node_compose_key_after()`. Top-level lifecycle calls are `xbc_init()`, `xbc_get_info()`, `_xbc_exit()`, and `xbc_exit()`. `xbc_get_embedded_bootconfig()` is present only with `CONFIG_BOOT_CONFIG_EMBED`.

Control flow: Boot code detects appended or embedded bootconfig, validates checksum/magic/size externally, calls `xbc_init()` on the buffer, then consumers traverse key/value nodes with find helpers or iterator macros. Key-only entries return zero-length strings with NULL value-node pointers. Cleanup calls `_xbc_exit(false)` through `xbc_exit()`.

State/persistence: Parser state is early-init global/static state managed by `xbc_init()` and `_xbc_exit()`. Nodes store offsets/indices into parser-managed data; no long-term persistence is promised after cleanup. Most APIs are annotated `__init`.

Dependencies/integration: Kernel mode includes `linux/kernel.h` and `linux/types.h`; non-kernel inclusion is reserved for bootconfig tooling. Integrates with initrd assembly, early command-line handling, and embedded bootconfig options.

Risks/test signals: Risks include malformed nesting, array/value confusion, off-by-one in packed 15-bit data offsets, key composition truncation, and userspace tool drift. Test signals include `tools/bootconfig` parser tests, booting with appended and embedded configs, malformed checksum/magic cases, array iteration, max depth/key length/data size boundaries, and early-boot memory sanitizer coverage where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bootconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bootmem_info.h -->
# sources/distributed-fs/ceph-client/include/linux/bootmem_info.h

Purpose: Provides memory-hotplug bootmem metadata helpers for tracking memblock-allocated page structures and freeing them correctly when sections or node metadata are released. The header abstracts whether the architecture supports storing bootmem metadata in `page->private`.

Important APIs/types/functions: `enum bootmem_type` identifies `SECTION_INFO`, `MIX_SECTION_INFO`, and `NODE_INFO` metadata, with min/max bounds for hotplug users. With `CONFIG_HAVE_BOOTMEM_INFO_NODE`, APIs include `register_page_bootmem_info_node()`, `register_page_bootmem_memmap()`, `get_page_bootmem()`, and `put_page_bootmem()`. Inline helpers decode low bits of `page->private` with `bootmem_type()` and the shifted info payload with `bootmem_info()`. `free_bootmem_page()` validates a reference count of 2 and only releases section/mixed-section metadata via `put_page_bootmem()`.

Control flow: Memory initialization registers pgdat and memmap pages as bootmem-backed metadata. Hotplug/removal code later checks `page->private`, drops metadata references, and returns eligible reserved pages to the buddy allocator. Without config support, registration is a no-op and `free_bootmem_page()` directly tells kmemleak about the physical page and calls `free_reserved_page()`.

State/persistence: State is encoded in `struct page::private`; low 4 bits are the type and upper bits are the info value. This persists for reserved metadata pages until released. The fallback path carries no encoded metadata.

Dependencies/integration: Depends on core MM, memblock/buddy allocator behavior, kmemleak, `pglist_data`, `struct page`, PFN translation, and memory-hotplug section management.

Risks/test signals: Risks include corrupting `page->private`, freeing a page with the wrong refcount/type, leaking memmap pages, or double-freeing reserved memory when config variants diverge. Test signals include memory hotplug add/remove cycles, sparsemem section teardown, kmemleak scans, VM_BUG_ON coverage under debug kernels, and boot tests on architectures with and without `CONFIG_HAVE_BOOTMEM_INFO_NODE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bootmem_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bottom_half.h -->
# sources/distributed-fs/ceph-client/include/linux/bottom_half.h

Purpose: Defines the small bottom-half disable/enable API used to prevent softirq processing in critical sections. It hides differences between normal kernels, PREEMPT_RT, and IRQ flag tracing.

Important APIs/types/functions: `local_bh_disable()` calls `__local_bh_disable_ip(_THIS_IP_, SOFTIRQ_DISABLE_OFFSET)`. On non-RT/non-trace builds, `__local_bh_disable_ip()` is an inline `preempt_count_add(cnt)` plus compiler barrier. On PREEMPT_RT or IRQ trace builds it is an out-of-line function so extra tracking/locking semantics can be implemented. `_local_bh_enable()` and `__local_bh_enable_ip()` are externs, with `local_bh_enable_ip()` and `local_bh_enable()` as inline wrappers. `local_bh_blocked()` reports PREEMPT_RT state and is false otherwise.

Control flow: Callers bracket a softirq-sensitive region with `local_bh_disable()` and `local_bh_enable()`. The disable side increments preempt/softirq state immediately; the enable side may process pending softirqs or perform RT-specific unlock behavior in the implementation.

State/persistence: State is per-task/per-CPU preemption count and, on RT, extra bottom-half blocking state. It is intentionally transient and must be balanced.

Dependencies/integration: Depends on instruction pointer capture, preempt count definitions, softirq offset constants, PREEMPT_RT, and trace IRQFLAGS infrastructure. It is consumed by networking, timers, and any code needing bottom-half exclusion.

Risks/test signals: Risks are unbalanced disable/enable calls, sleeping in non-RT bottom-half-disabled regions, incorrect call-site IP for lockdep/trace diagnostics, and assuming RT semantics match non-RT. Test signals include lockdep, preempt-count underflow warnings, softirq latency tests, PREEMPT_RT boot/runtime tests, and networking stress with lockdep and IRQ tracing enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bottom_half.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf-cgroup-defs.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf-cgroup-defs.h

Purpose: Defines the cgroup BPF attachment type namespace and the per-cgroup BPF state container used by cgroup hooks. It is split from `bpf-cgroup.h` to provide definitions without pulling the full runtime wrapper surface.

Important APIs/types/functions: `enum cgroup_bpf_attach_type` enumerates ingress/egress skb hooks, socket create/release, sock_ops, device, bind/connect/sendmsg/recvmsg/getpeername/getsockname, sysctl, getsockopt/setsockopt, and optional per-cgroup LSM slots. `CGROUP_LSM_NUM` is 10 only with `CONFIG_BPF_LSM`, otherwise 0, and `MAX_CGROUP_BPF_ATTACH_TYPE` sizes arrays. `struct cgroup_bpf` stores RCU-protected effective program arrays per attach type, attached program lists, flags, revision counters, shared storage list, inactive temporary array for attach/detach rebuilds, a percpu refcount, and work item for release.

Control flow: Cgroup creation embeds this structure. Attach/detach operations update `progs[]`, rebuild `effective[]`, advance revisions, and use `inactive` as a staging array. Cgroup removal drops refs and schedules release work after the refcount drains.

State/persistence: State is per-cgroup and persists for the lifetime of the cgroup. Effective arrays are RCU-read by hot paths; program lists and flags are management state. When `CONFIG_CGROUP_BPF` is disabled, `struct cgroup_bpf` is empty.

Dependencies/integration: Depends on lists, percpu refs, workqueues, `struct bpf_prog_array`, and cgroup core. It integrates with socket, device, sysctl, and LSM hook call sites via `bpf-cgroup.h`.

Risks/test signals: Risks include attach type enum ordering mismatches with UAPI conversion, RCU lifetime bugs in effective arrays, stale revisions, release-work races, and optional LSM slot sizing errors. Test signals include cgroup BPF selftests for attach/query/detach, cgroup deletion while programs run, multi/override attach flags, and BPF LSM enabled/disabled build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf-cgroup-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf-cgroup.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf-cgroup.h

Purpose: Provides the runtime API and fast-path macros for executing BPF programs attached to cgroups. It maps UAPI attach types to internal cgroup attach slots, defines cgroup storage structures, declares attach/query operations, and gives networking/device/sysctl call sites cheap static-key-guarded wrappers.

Important APIs/types/functions: `to_cgroup_bpf_attach_type()` maps `enum bpf_attach_type` to `enum cgroup_bpf_attach_type`. `cgroup_bpf_enabled_key[]` and `cgroup_bpf_enabled()` gate hot paths with static branches. `struct bpf_cgroup_storage` links per-program storage to a cgroup and map through rb/list nodes and RCU. `struct bpf_prog_list` carries a program/link plus cgroup storage slots and attach flags. Declared execution functions include skb, sock, sockaddr, sock_ops, device, sysctl, setsockopt, and getsockopt filters. Macros such as `BPF_CGROUP_RUN_PROG_INET_INGRESS()`, `BPF_CGROUP_RUN_PROG_INET_BIND_LOCK()`, and `BPF_CGROUP_RUN_PROG_GETSOCKOPT()` perform enable checks, socket fullsock validation, locking where needed, and call the underlying executor.

Control flow: Subsystems call a macro at hook points. The macro first checks the static key and often `cgroup_bpf_sock_enabled()`, then invokes the correct `__cgroup_bpf_run_filter_*()` implementation. Management paths call `cgroup_bpf_prog_attach()`, `cgroup_bpf_prog_detach()`, `cgroup_bpf_link_attach()`, and `cgroup_bpf_prog_query()`.

State/persistence: Per-cgroup effective arrays live in `struct cgroup_bpf`; storage objects persist per attached program/map/cgroup and are RCU-freed. Static keys reflect whether any program of a given attach type exists. With `CONFIG_CGROUP_BPF` disabled, all wrappers compile to inert stubs returning pass/default values or `-EINVAL`.

Dependencies/integration: Integrates with sockets, sk_buffs, sysctl, device cgroups, sockptr, cgroup core, BPF maps/progs/links, and TCP bypass hooks.

Risks/test signals: Risks are incorrect default return semantics, missing socket locking, cgroup storage lifetime leaks, attach type conversion gaps, and bypass logic around getsockopt. Test signals include BPF cgroup selftests across all attach types, socket bind/connect/sendmsg/recvmsg scenarios, sysctl write filtering, device permission checks, link update/detach tests, cgroup teardown under traffic, and disabled-config build tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf-cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf-netns.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf-netns.h

Purpose: Defines the network-namespace BPF attachment management interface for hooks whose scope is a `struct net`, currently flow dissector and socket lookup. It provides attach-type conversion and configuration-dependent stubs.

Important APIs/types/functions: `to_netns_bpf_attach_type()` maps `BPF_FLOW_DISSECTOR` and `BPF_SK_LOOKUP` to internal `NETNS_BPF_*` values, returning `NETNS_BPF_INVALID` for unsupported attach types. `netns_bpf_mutex` serializes updates to netns BPF state. With `CONFIG_NET`, exported functions are `netns_bpf_prog_query()`, `netns_bpf_prog_attach()`, `netns_bpf_prog_detach()`, and `netns_bpf_link_create()`.

Control flow: BPF syscall attach/link paths convert a UAPI attach type, lock `netns_bpf_mutex`, and update per-netns BPF state in `net/netns/bpf.h`. Runtime hooks then consult the per-namespace program/link state from networking paths.

State/persistence: State is per-network namespace and protected for updates by the global mutex. The header itself does not own state beyond declaring the mutex. Without `CONFIG_NET`, all operations return `-EOPNOTSUPP`.

Dependencies/integration: Depends on net namespace BPF definitions, UAPI BPF attach types, and BPF program/link syscalls. Integrates with flow dissector and `sk_lookup` networking paths.

Risks/test signals: Risks include attach-type mismatches, cross-netns leakage, failure to hold `netns_bpf_mutex` during updates, and stale links on namespace teardown. Test signals include BPF selftests for flow dissector and sk_lookup in multiple network namespaces, namespace create/delete while links exist, attach/query/detach error paths, and `CONFIG_NET=n` build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf-netns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf.h

Purpose: This is the central in-kernel BPF contract. It defines map, program, link, trampoline, dispatcher, dynptr, struct_ops, iterator, token, offload, BTF-field, helper-prototype, and execution APIs used by BPF syscall handling, verifier, JITs, networking hooks, tracing hooks, LSM, and map implementations.

Important APIs/types/functions: `struct bpf_map_ops` is the map vtable for syscall operations, program-visible operations, fd-backed maps, BTF validation, prog-poke tracking, mmap/poll, local-storage hooks, redirects, callbacks, and memory usage. `struct bpf_map` carries type, sizes, BTF metadata, ref/user/write counts, ownership, freeze state, memcg/NUMA data, internal field records, and cookie/name. BTF field helpers describe spin locks, timers, kptrs, graph nodes, refcounts, workqueues, user pointers, and task work, and provide value init/copy/zero/free behavior that intentionally skips or preserves internal fields. `enum bpf_arg_type`, `enum bpf_return_type`, and `enum bpf_reg_type` encode verifier helper contracts and pointer modifiers. `struct bpf_func_proto`, `struct bpf_verifier_ops`, `struct bpf_prog_ops`, and offload ops define verification/test-run hooks. `struct bpf_prog_aux` and `struct bpf_prog` hold all program metadata, JIT state, used maps/BTFs, attach target, trampoline/offload state, storage, stream logs, and instruction arrays. `struct bpf_link` and `struct bpf_link_ops` abstract attach lifetime. Trampoline and dispatcher structs/macros model fentry/fexit/struct_ops call patching and static-call optimization. Runtime helpers include program-array execution, map/prog/link refcount APIs, object pin/get, iterator registration, test-run entry points, dev/cpu map redirects, dynptr accessors, token delegation, kfunc lookup, and many exported helper prototypes.

Control flow: BPF syscall code creates maps/programs/links, initializes metadata from `union bpf_attr`, calls `bpf_check()` for verification, optionally JITs or offloads programs, assigns IDs/fds, and publishes objects. Runtime call sites run single programs or `bpf_prog_array` lists under RCU/tasks-trace RCU with per-CPU recursion/instrumentation guards. Attach paths use links, trampoline linkage, cgroup/netns helpers, or map-contained program arrays. Cleanup paths use refcounts, usercnts, work items, RCU, tasks-trace RCU, and module refs depending on object type.

State/persistence: BPF objects persist as refcounted kernel objects exposed by fds, bpffs pins, links, map ownership, and subsystem attachment points. Program arrays are RCU-replaced. Maps can be frozen, have memcg accounting, store BTF records, and carry live internal objects. Tokens persist delegated capability masks tied to user namespaces. Many stubs return `-EOPNOTSUPP` or inert behavior when `CONFIG_BPF_SYSCALL`, `CONFIG_BPF_JIT`, `CONFIG_NET`, `CONFIG_INET`, or `CONFIG_KEYS` are absent.

Dependencies/integration: Pulls in UAPI BPF/filter, BTF, crypto hash, files, memory accounting, workqueues, modules, kallsyms, static calls, CFI, RCU trace, sockets/net devices, perf, cgroups, LSM, keyrings, and architecture JIT/trampoline hooks. `bpf_types.h` expands program/map/link operation externs.

Risks/test signals: Risks are broad: verifier contract drift, unsafe pointer modifier interpretation, refcount/RCU lifetime bugs, map value internal-field copying mistakes, trampoline/JIT patching errors, token capability bypass, memcg/accounting leaks, disabled-config stub mismatches, and program-array concurrency issues. Test signals include kernel BPF selftests, verifier tests, JIT tests on multiple architectures, bpftool map/prog/link lifecycle, cgroup/netns/LSM/tracing/struct_ops tests, KASAN/KCSAN/KMSAN/lockdep/RCU torture, and config-matrix builds with BPF syscall/JIT/net/features toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_crypto.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf_crypto.h

Purpose: Declares a pluggable crypto provider interface for BPF crypto kfunc/helper support. It lets crypto implementations register an algorithm family with BPF without exposing concrete transform internals.

Important APIs/types/functions: `struct bpf_crypto_type` contains callbacks to allocate/free transforms, check algorithm availability, set key and authentication size, encrypt/decrypt buffers with an IV, report IV/state sizes, read transform flags, hold the owning module, and publish a short provider name. `bpf_crypto_register_type()` and `bpf_crypto_unregister_type()` manage provider registration.

Control flow: A provider fills `bpf_crypto_type`, registers it, and BPF crypto logic later resolves algorithms through the registered type, allocates transforms, configures keys/auth size, invokes encrypt/decrypt, and releases the transform. Module ownership is expected to pin provider code while used.

State/persistence: Provider registrations persist until unregister. Per-transform state is opaque `void *tfm` owned by the provider callbacks. The type structure is const from the caller perspective and includes module/name identity.

Dependencies/integration: Depends on kernel crypto providers, BPF kfunc/helper implementation, module lifetime management, and UAPI-visible BPF crypto behavior elsewhere.

Risks/test signals: Risks include module unload races, mismatched IV/auth/key sizes, algorithm-name validation issues, transform leaks, and provider callback behavior differences. Test signals include BPF crypto selftests for register/unregister, encrypt/decrypt known-answer vectors, unsupported algorithm handling, module unload under active use, and fault injection for allocation/setkey failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_lirc.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf_lirc.h

Purpose: Declares BPF attach management for LIRC mode2 infrared programs. It isolates optional LIRC BPF support behind `CONFIG_BPF_LIRC_MODE2`.

Important APIs/types/functions: With the config enabled, `lirc_prog_attach()`, `lirc_prog_detach()`, and `lirc_prog_query()` implement syscall-facing attach, detach, and query operations using `union bpf_attr` and `struct bpf_prog`. With the config disabled, inline stubs return `-EINVAL`.

Control flow: BPF syscall paths route LIRC attach-type operations to these functions. Attach installs a BPF program on a LIRC device/hook, detach removes it, and query reports attached program IDs/counts.

State/persistence: Attachment state is maintained in the LIRC subsystem implementation, not in this header. Program refs should persist while attached and drop on detach/device teardown.

Dependencies/integration: Depends on UAPI BPF definitions, LIRC mode2 driver support, and BPF program lifetime rules.

Risks/test signals: Risks include invalid attr validation, device lifetime races, incorrect stub errno expectations, and program ref leaks. Test signals include BPF LIRC selftests or IR-device tests, attach/query/detach cycles, device unplug while attached, and config builds with `CONFIG_BPF_LIRC_MODE2` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_lirc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_local_storage.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf_local_storage.h

Purpose: Defines the generic object-local BPF storage infrastructure used by socket, task, inode, cgroup-related, or other local-storage maps. It lets BPF maps define storage value size while the target object owns the per-object mini-map/list of storage elements.

Important APIs/types/functions: `struct bpf_local_storage_map` embeds `struct bpf_map`, has per-bucket hash/list locks, element size, and cache index. `struct bpf_local_storage_elem` links one storage value into both the map bucket and owning object's `struct bpf_local_storage`; atomic state bits track map unlink, storage unlink, and deferred free. `struct bpf_local_storage` has a small RCU cache, element list, owner pointer, RCU head, raw/q spinlock, mem charge, and owner refcount. `bpf_local_storage_lookup()` performs an RCU cache lookup first, then scans the per-object list and optionally refreshes the cache. Allocation/update/free APIs manage map validation, element allocation/linking/unlinking, object storage allocation, BTF checks, and memory usage.

Control flow: Map creation validates attributes and allocates buckets/cache index. On update, storage elements are allocated, linked to the owner storage and map bucket, and charged to the owner. Lookup from BPF or syscall uses the owner storage and map pointer as key. Object teardown calls `bpf_local_storage_destroy()`; map teardown unlinks all elements.

State/persistence: Storage values persist for the lifetime of the owner object or map, whichever unlinks first. RCU protects lookups; bucket locks and object locks protect mutations. The cache is an optimization and can be stale until RCU-safe replacement.

Dependencies/integration: Depends on core BPF map definitions, filter/BTF support, RCU hlist, hash/list primitives, BPF memory allocator, and raw/q spinlocks. Integrates with concrete map ops through `map_local_storage_charge`, `map_local_storage_uncharge`, and `map_owner_storage_ptr`.

Risks/test signals: Risks include dual-owner unlink races, stale cache entries, mem-charge imbalance, owner refcount misuse, lock ordering between map buckets and object storage, and BTF value-size mistakes. Test signals include local storage selftests for sockets/tasks/inodes, concurrent update/delete/lookup, owner teardown under active lookup, map destruction with live owners, KCSAN/lockdep, and memory accounting assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_local_storage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_lsm.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf_lsm.h

Purpose: Declares BPF LSM hook entry points and helper interfaces for verifying and running BPF programs attached to Linux Security Module hooks. It also exposes inode local storage support and cgroup LSM shim helpers.

Important APIs/types/functions: Under `CONFIG_BPF_LSM`, `LSM_HOOK()` expansion declares `bpf_lsm_<hook>()` functions for every hook in `lsm_hook_defs.h`. `struct bpf_storage_blob` holds an RCU local-storage pointer for security blobs. `bpf_lsm_blob_sizes` identifies offsets in LSM blobs. `bpf_lsm_verify_prog()` validates BPF LSM programs. `bpf_lsm_is_sleepable_hook()` and `bpf_lsm_is_trusted()` classify hooks/programs. `bpf_inode()` computes the BPF storage blob inside `inode->i_security`. Inode storage helper prototypes, cgroup shim lookup, retval range lookup, and locked dentry xattr helpers are declared. Disabled stubs return false, NULL, or `-EOPNOTSUPP`.

Control flow: LSM dispatch invokes generated `bpf_lsm_*` hook functions. Program load calls verification helpers to enforce hook-specific constraints and return ranges. Inode lifecycle frees BPF inode storage. Cgroup LSM integration can locate a shim trampoline for per-cgroup LSM hooks.

State/persistence: BPF LSM storage is held in LSM security blobs and RCU-protected local storage. Hook program attachments and blob offsets persist while the BPF LSM facility and objects exist.

Dependencies/integration: Depends on scheduler types, core BPF/verifier APIs, LSM hooks/blobs, inode/dentry structures, BPF local storage, and optional cgroup BPF LSM slots.

Risks/test signals: Risks include wrong blob offset arithmetic, hook sleepability mismatches, verifier return-range mistakes, xattr locking misuse, and disabled-config behavior drift. Test signals include BPF LSM selftests, LSM hook coverage, inode storage get/delete/free tests, cgroup LSM attach tests, xattr helper tests under lockdep, and config builds without `CONFIG_BPF_LSM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_lsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_mem_alloc.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf_mem_alloc.h

Purpose: Declares the BPF memory allocator abstraction used for fast fixed-size and variable-size object allocation, including percpu modes and RCU-delayed freeing. It separates BPF map/program allocation patterns from raw slab APIs.

Important APIs/types/functions: `struct bpf_mem_alloc` holds percpu cache groups, optional fixed-size cache, object cgroup, percpu mode flag, destruction work, and destructor context/free callbacks. `bpf_mem_alloc_init()` initializes fixed-size or variable-size allocators; `bpf_mem_alloc_percpu_init()` and `bpf_mem_alloc_percpu_unit_init()` handle percpu allocation. `bpf_mem_alloc_destroy()` drains resources, `bpf_mem_alloc_set_dtor()` installs destructors, `bpf_mem_alloc_check_size()` validates sizes, and the allocation families include `bpf_mem_alloc/free/free_rcu()` plus fixed-cache `bpf_mem_cache_alloc/free/free_rcu/raw_free/alloc_flags()`.

Control flow: A BPF subsystem initializes an allocator, allocates objects during map/program operations, frees immediately or after RCU depending on reader lifetime, and destroys the allocator after all users drain. Destructor callbacks run during delayed object release.

State/persistence: Allocator state persists in the owning map/subsystem. Per-CPU caches improve allocation latency. `work` handles asynchronous destruction/drain. `objcg` ties allocations to memory cgroup accounting.

Dependencies/integration: Depends on compiler annotations, workqueues, percpu allocation internals, object cgroups, RCU lifetime expectations, and BPF map/local-storage users.

Risks/test signals: Risks include freeing objects before RCU readers finish, excessive percpu memory use, destructor context leaks, size-class validation mistakes, and memcg charging imbalance. Test signals include BPF allocator selftests, stress tests with concurrent map updates/deletes, RCU stall/leak checks, memcg accounting tests, fault injection on allocation, and allocator destroy under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_mem_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_mprog.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf_mprog.h

Purpose: Defines the generic BPF multi-program attachment framework used by hook sites that can host ordered sets of BPF programs, such as TC classifier links. It provides a double-buffered RCU-friendly array model plus attach/detach/query APIs with relative insertion semantics.

Important APIs/types/functions: `BPF_MPROG_MAX` caps array slots at 64, with one sentinel slot, so `bpf_mprog_max()` returns 63. `struct bpf_mprog_fp` stores fast-path program pointers; `struct bpf_mprog_cp` stores control-plane links. `struct bpf_mprog_entry` is one active array view, and `struct bpf_mprog_bundle` contains two entries, shared link metadata, a pending reference to release, revision counter, and count. Iteration macros `bpf_mprog_foreach_prog()` and `bpf_mprog_foreach_tuple()` use `READ_ONCE()` for fast-path program access. Inline helpers initialize bundles, select peer buffers, track count/revision, copy/clear/grow/shrink entries, write tuples with `WRITE_ONCE()`, and defer non-link program ref drops until after RCU grace. Core APIs are `bpf_mprog_attach()`, `bpf_mprog_detach()`, and `bpf_mprog_query()`.

Control flow: Callers hold an external hook-specific lock, fetch the active entry, call attach/detach to prepare `entry_new`, swap the hook pointer if needed, wait for inflight RCU readers, then call `bpf_mprog_commit()` to complete releases and bump revision. Fast paths enter RCU, iterate programs until NULL, run each program, and process return values.

State/persistence: The bundle persists for the attach location. Active entry pointers are RCU-published by the caller. Revision tracks observable updates and count tracks attached programs. Detached non-link program refs are held in `ref` until post-swap commit.

Dependencies/integration: Depends on core BPF program/link types, RCU discipline supplied by users, external locks such as RTNL for TCX, and capability checks via `bpf_net_capable()` for empty detach behavior.

Risks/test signals: Risks include forgetting external locking, swapping entries without a grace period, count/sentinel off-by-one errors, releasing program refs too early, and revision mismatch handling. Test signals include TC link/order selftests with BEFORE/AFTER/prepend/append, concurrent packet fast-path traffic during attach/detach, revision query tests, detach-empty permission tests, and KCSAN/RCU diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_mprog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_trace.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf_trace.h

Purpose: Provides a minimal BPF tracing include wrapper that brings XDP trace event definitions into BPF tracing-related compilation units.

Important APIs/types/functions: The file has no functions or structs of its own. Its only functional dependency is `#include <trace/events/xdp.h>`, guarded by `__LINUX_BPF_TRACE_H__`.

Control flow: Inclusion makes XDP tracepoint/event declarations available wherever this header is used. There is no runtime control flow in the header.

State/persistence: No state is defined.

Dependencies/integration: Integrates BPF-related code with kernel trace event definitions for XDP. It depends on the tracepoint header generation conventions and the XDP trace event provider.

Risks/test signals: Risks are limited to include-order or tracepoint-definition churn. Test signals include successful builds of BPF/XDP tracing code, trace event availability for XDP programs, and config combinations where tracing or XDP features are toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_types.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf_types.h

Purpose: Central macro inventory of BPF program types, map types, and link types. It is intentionally not directly included by ordinary users; instead other headers define `BPF_PROG_TYPE`, `BPF_MAP_TYPE`, and `BPF_LINK_TYPE` macros to generate declarations, tables, or switch cases from one authoritative list.

Important APIs/types/functions: Program entries map UAPI program types to internal operation names and context types, gated by configs such as `CONFIG_NET`, `CONFIG_CGROUP_BPF`, `CONFIG_BPF_EVENTS`, `CONFIG_BPF_LIRC_MODE2`, `CONFIG_INET`, `CONFIG_BPF_JIT`, `CONFIG_BPF_LSM`, and `CONFIG_NETFILTER_BPF_LINK`. Map entries enumerate array/hash/prog/perf/cgroup/local-storage/dev/cpu/xsk/sock/ringbuf/bloom/user-ringbuf/arena/insn-array and other map ops. Link entries enumerate raw tracepoint, tracing, cgroup, iterator, netns, XDP, netfilter, TCX, netkit, sockmap, perf event, kprobe/uprobe multi, and struct_ops links.

Control flow: This file is compile-time data. Consumers include it after defining macros to emit extern declarations in `bpf.h`, operation tables in BPF core, or string/metadata mappings elsewhere.

State/persistence: No runtime state. Its ordering and conditional presence influence compiled kernel capability surfaces and generated arrays.

Dependencies/integration: Integrates BPF UAPI enum values with internal ops symbols such as `sk_filter_prog_ops`, `array_map_ops`, or `raw_tracepoint` link ops. Depends heavily on Kconfig guards matching implementation availability.

Risks/test signals: Risks include forgetting to add new types to this inventory, using the wrong context type, mismatching config guards, or breaking macro consumers by changing entry shape. Test signals include allconfig/allyesconfig/randconfig builds, BPF syscall feature probes, bpftool feature output, selftests for every new prog/map/link type, and compile failures from missing ops externs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_verifier.h -->
# sources/distributed-fs/ceph-client/include/linux/bpf_verifier.h

Purpose: Defines the verifier’s internal abstract state, metadata, logging, CFG/liveness structures, and exported helper functions used by verifier and fixup passes. It is the structural backbone for proving BPF program safety before execution or JIT compilation.

Important APIs/types/functions: Limits such as `BPF_MAX_VAR_OFF`, `BPF_MAX_VAR_SIZ`, `TMP_STR_BUF_LEN`, and `INSN_BUF_SIZE` bound analysis. `struct bpf_reg_state` models each register’s type, map/BTF/memory/dynptr/iterator metadata, scalar tnum and min/max bounds, IDs for null/reference/range propagation, frame ownership, subregister definition, and precision flag. Stack state uses `enum bpf_stack_slot_type`, `struct bpf_stack_state`, and 4-byte liveness masks. `struct bpf_reference_state` tracks acquired pointer/IRQ/lock resources. `struct bpf_func_state` models a call frame, register set, callback metadata, and stack. `struct bpf_verifier_state` links frames, references, branch exploration counts, locks, RCU state, jump history, DFS depth, and loop/callback depth. `struct bpf_insn_aux_data` stores per-instruction map pointers, call immediates, ALU sanitization, BTF vars, jump tables, kfunc metadata, constant register facts, and fixup flags. `struct bpf_verifier_env` aggregates the program, ops, explored-state lists, used maps/BTFs, CFG arrays, subprogram info, logs, counters, scratch buffers, liveness, SCC info, and successor tables.

Control flow: `bpf_check()` allocates/populates a verifier environment, validates BTF and attach targets, builds CFG/postorder/SCC data, symbolically executes instructions through verifier states, prunes equivalent states, tracks references/locks/RCU, marks precision through backtracking, validates helpers/kfuncs/context accesses, then runs fixup/optimization/JIT prep passes. Helper inlines identify helper/pseudo/kfunc calls, mark prune/checkpoint/callback/jump points, track scratched registers/stack slots, and compute trampoline keys.

State/persistence: Verifier state is per-program-load and freed after verification, while selected outputs persist into `bpf_prog_aux`: used maps/BTFs, kfunc tables, subprogram metadata, stack depth, line info, JIT/fixup metadata, and flags. Logs persist only through the user-provided verifier log buffer.

Dependencies/integration: Depends on `bpf.h` type contracts, BTF, filter stack limits, `tnum`, offload verifier hooks, fixups, JIT subprogram logic, kfunc metadata, trampoline attach target checks, and map direct-read logic.

Risks/test signals: Risks are verifier soundness bugs, imprecise state pruning, reference/lock leaks, loop/SCC mishandling, ALU speculation sanitization mistakes, stack liveness errors, kfunc argument metadata drift, and log truncation/accounting bugs. Test signals include exhaustive verifier selftests, malicious/unprivileged program rejection tests, precision and loop tests, kfunc/dynptr/iterator/local-storage tests, JIT equivalence tests, verifier log tests, syzkaller, KMSAN/KASAN/KCSAN, and config builds with offload/JIT/features toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpf_verifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpfptr.h -->
# sources/distributed-fs/ceph-client/include/linux/bpfptr.h

Purpose: Provides `bpfptr_t`, a kernel/userspace pointer wrapper used by BPF syscall and helper paths that may receive data from either kernel memory or user memory. It aliases `sockptr_t` and adds BPF-named constructors and copy/string helpers.

Important APIs/types/functions: `bpfptr_is_kernel()` reads the address-space tag. `KERNEL_BPFPTR()` and `USER_BPFPTR()` construct tagged pointers. `make_bpfptr()` converts a raw 64-bit address plus kernel/user flag. `bpfptr_is_null()` and `bpfptr_add()` inspect and adjust pointers. `copy_from_bpfptr_offset()` copies from user with `copy_from_user()` or from kernel with `copy_from_kernel_nofault()`, while `copy_from_bpfptr()` uses offset zero. `copy_to_bpfptr_offset()` delegates to `copy_to_sockptr_offset()`. `kvmemdup_bpfptr_noprof()` allocates a kernel buffer and copies from the source, with `kvmemdup_bpfptr()` wrapped in allocation hooks. `strncpy_from_bpfptr()` chooses kernel nofault or user string copy.

Control flow: Callers build a `bpfptr_t` from syscall/user or kernel context, validate sizes elsewhere, copy or duplicate data through these helpers, and receive `-EFAULT`/ERR_PTR on bad memory or `-ENOMEM` on allocation failure.

State/persistence: No persistent state; the wrapper carries a pointer and `is_kernel` tag by value. Duplicated buffers persist until the caller frees them.

Dependencies/integration: Depends on memory management allocation helpers, `sockptr_t`, user access helpers, `copy_from_kernel_nofault()`, and BPF syscall argument parsing.

Risks/test signals: Risks include accidentally tagging user pointers as kernel, pointer arithmetic overflow, missing size validation before duplication, and treating nofault kernel copies as normal trusted loads. Test signals include BPF syscall tests for kernel/user attr paths, fault-injection for bad user pointers, KASAN/KMSAN usercopy checks, zero-length/null-pointer cases, and string-copy boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/bpfptr.h -->
