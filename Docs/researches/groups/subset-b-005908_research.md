# Research: subset-b-005908

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/prefetch.h -->
# sources/distributed-fs/ceph-client/include/linux/prefetch.h

Purpose: provides generic cache prefetch wrappers so common code can request read/write prefetching without depending directly on architecture intrinsics. It also exposes helper prefetches for byte ranges and page-address metadata.

Important APIs and types: `prefetch(x)` and `prefetchw(x)` default to `__builtin_prefetch()` unless an architecture supplies `ARCH_HAS_PREFETCH` or `ARCH_HAS_PREFETCHW`. `PREFETCH_STRIDE` defaults to `4 * L1_CACHE_BYTES`. `prefetch_range()` walks a buffer in stride increments when arch prefetch exists, and `prefetch_page_address()` prefetches `struct page` metadata only for page-virtual configurations.

Control flow: callers issue prefetches before touching memory on hot paths; architectures may replace the default macros with tuned instructions. The range helper is a simple loop over cacheline lookahead distance and intentionally has no effect on arches without an explicit prefetch implementation.

State and persistence: no state is stored and no data is modified. Prefetching is a transient CPU cache hint and must not be required for correctness.

Dependencies and integration points: depends on `asm/processor.h`, `asm/cache.h`, `L1_CACHE_BYTES`, and optional page virtual configuration. It integrates with list walking, networking, filesystem, and memory-management paths that want architecture-neutral prefetch hints.

Risks and test signals: risks are performance regressions from over-prefetching, relying on prefetch for ordering, and invalid arch definitions that fault on bad addresses. Test signals are build coverage across arches, microbenchmarks of streaming users, and fault-injection style calls with null/unmapped-looking addresses to confirm prefetch remains only a hint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/prefetch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/prime_numbers.h -->
# sources/distributed-fs/ceph-client/include/linux/prime_numbers.h

Purpose: declares generic prime-number helpers used by kernel code that needs prime table sizing, hash bucket choices, or arithmetic iteration.

Important APIs and types: `is_prime_number()` tests primality, `next_prime_number()` advances to the next prime at or after a seed, and `for_each_prime_number()` / `for_each_prime_number_from()` macros iterate primes up to a caller-provided maximum.

Control flow: iteration initializes `prime` from either `2` or the supplied `from`, then repeatedly calls `next_prime_number(prime)` until `prime > max`. The comments explicitly require `max < ULONG_MAX` and, for the `_from` form, `from < max` so iteration terminates.

State and persistence: no public state is defined here. Any implementation tables or caches live in the corresponding source file and are not exposed through this header.

Dependencies and integration points: depends only on `linux/types.h`. It is a small math helper for generic kernel subsystems and should remain independent of allocator or architecture state.

Risks and test signals: risks include infinite loops when callers pass boundary values, overflow near `ULONG_MAX`, and mismatch between primality and next-prime behavior. Test small primes/composites, `0`/`1`/`2`, upper-bound iteration termination, and word-size differences on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/prime_numbers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/printk.h -->
# sources/distributed-fs/ceph-client/include/linux/printk.h

Purpose: defines the kernel logging interface: loglevel parsing, `printk()` and `pr_*()` macros, deferred and ratelimited logging, printk indexing metadata, dump-stack/log-buffer hooks, console flushing helpers, and disabled-config stubs.

Important APIs and types: `printk_get_level()`, `printk_skip_level()`, and `printk_skip_headers()` parse `KERN_*` prefixes. `vprintk_emit()`, `_printk()`, `_printk_deferred()`, `printk_trigger_flush()`, `console_try_replay_all()`, `pr_flush()`, and `dump_stack*()` are the core function surface under `CONFIG_PRINTK`. `printk()`, `printk_deferred()`, `pr_emerg()` through `pr_info()`, `pr_debug()`, `printk_once()`, `pr_*_once()`, and `pr_*_ratelimited()` are macro wrappers. `struct pi_entry` and `__printk_index_emit()` populate `.printk_index` when `CONFIG_PRINTK_INDEX` is enabled. Hex dump helpers include `hex_dump_to_buffer()`, `print_hex_dump()`, and debug/devel variants.

Control flow: normal callers enter through `printk()` or `pr_*()`, which optionally emit index metadata and call `_printk()` with an embedded loglevel. The printk core records to the ring buffer and console delivery may happen immediately or later depending on console lock ownership. Ratelimited macros create per-callsite static `ratelimit_state`; once macros use `DO_ONCE_LITE`; dynamic debug routes `pr_debug()` and debug hex dumps through dynamic-debug metadata. Deferred logging and force-console sections expose narrow hooks for scheduler/timekeeping and panic-sensitive paths.

State and persistence: logging state is global kernel state: `console_printk[]`, `oops_in_progress`, `suppress_printk`, `devkmsg_log_str`, `printk_delay_msec`, `dmesg_restrict`, `kptr_restrict`, the log buffer, static ratelimit states, once flags, and printk index sections. Logs persist only as long as kernel log storage, pstore, or userspace capture retains them.

Dependencies and integration points: depends on kernel loglevel definitions, ratelimit types, once-lite, dynamic debug, consoles, `/dev/kmsg` file operations, vmcoreinfo, stack dump code, and non-blocking console support. It is one of the widest integration points in the kernel and is callable from normal, interrupt, panic, and sometimes NMI-adjacent contexts.

Risks and test signals: risks include format-string regressions, console recursion/deadlock, unsafe use of deferred sections with interrupts enabled, loglevel header parsing drift, disabled `CONFIG_PRINTK` stubs hiding side effects, ratelimit sharing through `printk_ratelimit()`, and printk-index section bloat. Test with `CONFIG_PRINTK`, `CONFIG_PRINTK_INDEX`, dynamic debug, `DEBUG`, and no-printk builds; exercise `/dev/kmsg`, panic/oops logging, rate-limited callsites, `pr_flush()` timeout behavior, and hex dump formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/prmt.h -->
# sources/distributed-fs/ceph-client/include/linux/prmt.h

Purpose: exposes ACPI Platform Runtime Mechanism Table support to generic callers that need to discover and invoke PRM handlers by GUID.

Important APIs and types: under `CONFIG_ACPI_PRMT`, `init_prmt()` initializes PRMT handling, `acpi_prm_handler_available()` checks for a handler GUID, and `acpi_call_prm_handler()` invokes a handler with a parameter buffer. Without the config, the functions become no-ops or return `false`/`-EOPNOTSUPP`.

Control flow: ACPI initialization calls `init_prmt()`, then drivers or platform code can check availability before calling a runtime handler. The header enforces a graceful disabled path so callers can compile independent of PRMT support.

State and persistence: no state is defined here; parsed ACPI table data and handler metadata live in the ACPI PRMT implementation. Handler calls may affect firmware/platform runtime state.

Dependencies and integration points: depends on `linux/uuid.h`, ACPI PRMT table parsing, and firmware-provided handler GUIDs. It integrates ACPI firmware services with kernel drivers needing platform runtime operations.

Risks and test signals: risks include calling unavailable handlers, malformed parameter buffers, firmware side effects, and config-disabled behavior not being checked. Test ACPI PRMT discovery, GUID lookup, successful and failing handler calls, bad buffers, and builds without `CONFIG_ACPI_PRMT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/prmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/proc_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/proc_fs.h

Purpose: declares the kernel-facing procfs API for creating, removing, and operating `/proc` entries, including seq-file helpers, network namespace proc entries, mount policy state, BPF iterator integration, pidfd helpers, and disabled-config stubs.

Important APIs and types: `struct proc_ops` is the file-operation table for proc entries, with read/write/seek/poll/ioctl/mmap callbacks and flags such as `PROC_ENTRY_PERMANENT`, `PROC_ENTRY_proc_read_iter`, and `PROC_ENTRY_FORCE_LOOKUP`. `struct proc_fs_info` stores per-superblock pid namespace, `hide_pid`, `pidonly`, and group policy. Creation helpers include `proc_symlink()`, `_proc_mkdir()`, `proc_mkdir*()`, `proc_create*()`, `proc_create_seq*()`, `proc_create_single*()`, and network variants such as `proc_create_net_data()`. Removal and metadata helpers include `proc_remove()`, `remove_proc_entry()`, `remove_proc_subtree()`, `proc_set_size()`, `proc_set_user()`, `pde_data()`, and `proc_get_parent_data()`.

Control flow: subsystems create directories or files under a parent `proc_dir_entry`, optionally attach private data, and supply either `proc_ops`, `seq_operations`, or single-show callbacks. Procfs dispatches VFS operations through `struct proc_ops`; network helpers bind namespace state; cleanup must remove entries before backing data disappears. When procfs is disabled, creation returns `NULL` and removals are no-ops, forcing callers to tolerate absence.

State and persistence: proc entries are in-memory VFS objects tied to procfs lifetime; `proc_fs_info` is per mount/superblock and RCU-freed. The files expose live kernel state rather than persistent storage. Private `pde_data()` state remains owned by the registering subsystem.

Dependencies and integration points: depends on VFS, seq_file, pid namespaces, network namespaces, BPF iterators, architecture `/proc` status hooks, and proc namespace helpers. It is central to diagnostic and control files used by drivers, filesystems, networking, and process introspection.

Risks and test signals: risks include use-after-free when removing proc entries after private data is freed, missing `proc_lseek`, wrong hidepid/pid namespace behavior, callback ABI mismatches, and untested disabled `CONFIG_PROC_FS` stubs. Test creation/removal races, module unload with open files, seq-file iteration, netns teardown, BPF iterator init/fini, pidfd conversion, hidepid mount options, and no-procfs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/proc_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/proc_ns.h -->
# sources/distributed-fs/ceph-client/include/linux/proc_ns.h

Purpose: defines procfs namespace operation descriptors and namespace inode allocation helpers used for `/proc/<pid>/ns/*` and nsfs integration.

Important APIs and types: `struct proc_ns_operations` names a namespace type and provides `get`, `put`, `install`, `owner`, and `get_parent` callbacks. Global operation tables are declared for net, UTS, IPC, PID, user, mount, cgroup, and time namespaces, including child namespace variants. Initial inode numbers map to UAPI nsfs constants, and `proc_alloc_inum()` / `proc_free_inum()` manage proc namespace inode numbers when procfs is enabled. `get_proc_ns(inode)` returns the stored `ns_common`.

Control flow: proc namespace files use the operation table to acquire a task's namespace, expose it through nsfs, install a namespace during setns-like operations, and release references. Inode allocation produces stable-looking namespace identifiers for proc/ns entries; disabled procfs returns a harmless inode value.

State and persistence: this header exposes namespace references stored in inode private data. Namespace objects are refcounted runtime state and persist only while referenced by tasks, files, mounts, or nsfs handles.

Dependencies and integration points: depends on `linux/nsfs.h`, UAPI namespace inode constants, namespace implementations, user namespaces, procfs, and setns/open-related-namespace paths.

Risks and test signals: risks include reference leaks in `get`/`put`, wrong owner namespace checks, stale `inode->i_private`, and inode number allocation collisions. Test `/proc/<pid>/ns` open/readlink/setns flows, namespace teardown with open fds, user namespace permission checks, and builds without procfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/proc_ns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/processor.h -->
# sources/distributed-fs/ceph-client/include/linux/processor.h

Purpose: provides generic busy-wait primitives layered over architecture `cpu_relax()` hooks, allowing arch code to optimize spin begin/end and relax behavior.

Important APIs and types: `spin_begin()`, `spin_cpu_relax()`, and `spin_end()` are default no-op/`cpu_relax()` macros unless an architecture overrides them. `spin_until_cond(cond)` waits until a condition becomes true, avoiding the spin setup in the common already-true case.

Control flow: callers wrap very short expected waits with `spin_until_cond()` or explicit begin/relax/end loops. The loop calls `spin_cpu_relax()` repeatedly and then `spin_end()` once the condition is met.

State and persistence: no state is owned here. Any state observed by `cond` belongs to the caller and must have its own memory-ordering rules.

Dependencies and integration points: depends on `asm/processor.h` and architecture-specific CPU relax/yield implementations. It is used by low-level synchronization code where sleeping would be more expensive than a short spin.

Risks and test signals: risks include unbounded spinning, missing barriers in the condition, calling blocking or locking code inside the loop, and poor behavior under virtualization when the owner is not running. Test arch overrides, lock contention microbenchmarks, and race-sensitive users with lockdep/KCSAN-style instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/profile.h -->
# sources/distributed-fs/ceph-client/include/linux/profile.h

Purpose: declares the legacy kernel profiling hooks for CPU, scheduler, and KVM profiling, including procfs exposure when profiling and procfs are enabled.

Important APIs and types: profiling type bits are `CPU_PROFILING`, `SCHED_PROFILING`, and `KVM_PROFILING`. `prof_on` gates profiling. APIs include `profile_init()`, `profile_setup()`, `profile_tick()`, `setup_profiling_timer()`, `profile_hits()`, and inline `profile_hit()`. `create_proc_profile()` creates procfs output when both relevant configs are enabled.

Control flow: boot/setup config enables a profiling type, periodic or event paths call `profile_tick()` / `profile_hit()`, and `profile_hit()` fast-paths out unless `prof_on` matches the event type. Multiple hits can be accumulated through `profile_hits()`.

State and persistence: profiling data is in-memory diagnostic state, optionally visible through procfs. It is not persistent across boot.

Dependencies and integration points: depends on kernel init, cache annotations, procfs, timer setup, scheduler/tick paths, and optional KVM profiling users.

Risks and test signals: risks include hot-path overhead when disabled, incorrect `prof_on` type matching, procfs exposure mismatches, and timer multiplier errors. Test enabled and disabled profiling configs, proc profile creation, boot parameter parsing, and event accounting under CPU and scheduler load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/profile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/projid.h -->
# sources/distributed-fs/ceph-client/include/linux/projid.h

Purpose: defines type-safe project ID handling for filesystems, separating userspace `projid_t` values from kernel-internal `kprojid_t` values and supporting user namespace mappings.

Important APIs and types: `projid_t` is the userspace-style scalar, while `kprojid_t` wraps the kernel value. Helpers include `__kprojid_val()`, `KPROJIDT_INIT()`, `INVALID_PROJID`, `OVERFLOW_PROJID`, `projid_eq()`, `projid_lt()`, and `projid_valid()`. With user namespaces, `make_kprojid()`, `from_kprojid()`, `from_kprojid_munged()`, and `kprojid_has_mapping()` perform namespace translation; without them they are identity mappings with overflow munging.

Control flow: filesystems convert incoming project IDs from a user namespace into `kprojid_t`, store/compare the internal value, and convert back for presentation. The munged form substitutes `OVERFLOW_PROJID` when no mapping exists.

State and persistence: no state is stored here, but project IDs are persistent filesystem metadata in quota/project-inheritance users. Namespace mapping state belongs to `struct user_namespace`.

Dependencies and integration points: depends on kernel UID-sized types and user namespace mapping code. It integrates quota, filesystem inode attributes, idmapped presentation, and user namespace permissions.

Risks and test signals: risks include confusing `projid_t` and `kprojid_t`, failing to check mappings, storing unmapped values, and overflow behavior differences with `CONFIG_USER_NS`. Test project quota operations across user namespaces, invalid project IDs, serialization/deserialization of inode metadata, and user-ns disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/projid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/property.h -->
# sources/distributed-fs/ceph-client/include/linux/property.h

Purpose: provides the unified firmware-node and device-property interface used by drivers to read DT/ACPI/software-node properties, traverse child nodes and graph endpoints, manage software nodes, and discover device connections independent of firmware source.

Important APIs and types: `enum dev_prop_type`, `struct property_entry`, `struct software_node_ref_args`, and `struct software_node` describe typed property data and software-provided firmware nodes. Device and fwnode readers cover presence, bools, integer arrays/scalars, strings, string matching, reference args, IRQs, DMA attributes, PHY mode, I/O mapping, and match data. Traversal helpers include parent and child iteration macros, scoped cleanup variants, named child lookup/counts, and graph endpoint/remote endpoint helpers. Property constructors include `PROPERTY_ENTRY_*` and `SOFTWARE_NODE_REFERENCE()`. Software node lifecycle APIs include register/unregister group, create/remove fwnode, attach/remove device software node, and managed creation.

Control flow: a driver obtains `dev_fwnode(dev)` or a child fwnode, reads typed properties, traverses children/endpoints with reference release handled manually or by scoped macros, and may synthesize software nodes where firmware is incomplete. Graph helpers walk endpoints and remote ports for media/display-style topologies. Software node property arrays can be duplicated/freed and attached to devices for later property lookup.

State and persistence: property data is firmware or software-node state owned by firmware backends, device core, or registering drivers. Fwnode handles are reference-managed; software nodes persist until unregistered or removed. Properties describe hardware configuration and are not mutable runtime state unless a software node provider replaces them.

Dependencies and integration points: depends on `fwnode.h`, cleanup annotations, array/count macros, device core, ACPI/OF/software-node backends, IRQ mapping, device links/connections, graph bindings, PHY helpers, and DMA attribute code. It is a major integration layer for portable drivers.

Risks and test signals: risks include leaking fwnode references when breaking loops, wrong typed property sizes, inline vs pointer property lifetime bugs, graph endpoint reference leaks, firmware-backend semantic differences, and accidental use of unavailable child nodes. Test DT, ACPI, and software-node devices; property count/read error paths; scoped iteration early returns; graph remote endpoint parsing; software node register/unregister; and device-managed cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/property.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pruss_driver.h -->
# sources/distributed-fs/ceph-client/include/linux/pruss_driver.h

Purpose: declares the TI PRU-ICSS subsystem helper interface for PRUSS memory regions and configuration registers used by remoteproc-backed PRU clients.

Important APIs and types: enums describe GP mux selection, GPI modes, PRU core types, and PRUSS memory ranges. `struct pruss_mem_region` carries virtual, physical, and size information. `struct pruss` stores device/config mappings, regmap, memory region ownership, a mutex, and clock mux handles. APIs include `pruss_get()`, `pruss_put()`, `pruss_request_mem_region()`, `pruss_release_mem_region()`, GPMUX get/set, GPI mode setting, MII_RT enable, and XFR enable. Disabled builds return `-EOPNOTSUPP` or `ERR_PTR(-EOPNOTSUPP)`.

Control flow: a PRU remoteproc client obtains the parent PRUSS, requests a memory region, configures mux/mode or feature bits, uses the memory while holding ownership, then releases it and drops the PRUSS reference.

State and persistence: runtime state is the PRUSS device object, mapped memories, `mem_in_use[]` ownership, mutex serialization, and hardware configuration registers. Hardware settings persist until changed or reset by platform power management.

Dependencies and integration points: depends on remoteproc PRUSS IDs, regmap, clocks, device model, and TI PRUSS platform drivers. It integrates industrial Ethernet, real-time co-processor firmware, and PRU memory sharing.

Risks and test signals: risks include double allocation of PRUSS memory, SoC-specific mux value differences, unbalanced get/put, register writes racing without the PRUSS lock, and config-disabled callers mishandling `-EOPNOTSUPP`. Test concurrent memory requests, GPMUX/GPI programming on supported SoCs, remoteproc probe/remove, and non-PRUSS build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pruss_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psci.h -->
# sources/distributed-fs/ceph-client/include/linux/psci.h

Purpose: declares the ARM PSCI firmware interface used for CPU power management, suspend, hotplug, OS-initiated mode, and firmware discovery through device tree or ACPI.

Important APIs and types: power-state type constants distinguish standby and power-down. Functions include `psci_tos_resident_on()`, `psci_cpu_suspend_enter()`, `psci_power_state_is_valid()`, `psci_set_osi_mode()`, and `psci_has_osi_support()`. `struct psci_operations` holds firmware call callbacks for version, CPU suspend/off/on, migrate, affinity info, and migrate info type. `struct psci_0_1_function_ids` stores legacy function IDs. Init hooks cover DT and ACPI, with ACPI HVC discovery helpers.

Control flow: platform init discovers PSCI via DT or ACPI, fills `psci_ops`, then CPU hotplug/idle/suspend paths call those operations to transition cores or query affinity. OSI mode can be enabled when firmware supports OS-initiated coordination.

State and persistence: global `psci_ops` and discovered function IDs are runtime firmware interface state. CPU power state is hardware/firmware state, not persisted by this header.

Dependencies and integration points: depends on ARM SMCCC, init ordering, CPU idle/hotplug/suspend code, ACPI, DT, and secure firmware. It bridges generic kernel power management to platform firmware.

Risks and test signals: risks include invalid power-state encodings, wrong conduit selection, ACPI/DT discovery mismatch, firmware returning unexpected errors, and OSI mode coordination bugs. Test CPU on/off, suspend states, ACPI and DT boot paths, HVC/SMC conduits, and invalid state rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pse-pd/pse.h -->
# sources/distributed-fs/ceph-client/include/linux/pse-pd/pse.h

Purpose: defines the Power Sourcing Equipment controller interface for Ethernet PoDL and Clause 33 PoE/PSE management, including driver callbacks, ethtool status/config structures, power-budget support, IRQ notification helpers, and consumer APIs used by PHY/network code.

Important APIs and types: status/config types include `pse_control_config`, `pse_admin_state`, `pse_pw_status`, `pse_ext_state_info`, `pse_pw_limit_ranges`, and `ethtool_pse_control_status`. `struct pse_controller_ops` declares mandatory and optional per-PI callbacks for admin state, power detection, extended state, class, actual power, enable/disable, voltage, power limit, priority, and requested power. `struct pse_pi`, `struct pse_controller_dev`, `struct pse_irq_desc`, and `struct pse_ntf` model controller state, PIs, IRQ mapping, and notifications. Public APIs include `pse_controller_register()`, `devm_pse_controller_register()`, `devm_pse_irq_helper()`, `of_pse_control_get()`, `pse_control_put()`, ethtool get/set helpers, and type tests.

Control flow: a PSE controller driver fills `pse_controller_dev` and ops, registers it, optionally installs IRQ helper mapping, and exposes PSE controls referenced by PHY/device tree. Network ethtool paths acquire a `pse_control`, query status, enable/disable, adjust power limit, or set priority. Static budget evaluation can use PI priorities, requested power, and allocated power maintained by core logic.

State and persistence: state includes registered controller lists, requested PSE controls, PI device-tree mapping, regulator devices, admin-state shadowing, priority and allocated power fields, IRQ FIFO notifications, and hardware PSE state. Configuration affects hardware power delivery but is not inherently persistent across reset.

Dependencies and integration points: depends on ethtool UAPI/netlink enums, PHY devices, regulator framework, kfifo, workqueues, device tree, netlink extack, and controller drivers. It integrates Ethernet PHY management with PoE/PSE hardware.

Risks and test signals: risks include unit confusion between uA/mW, missing mandatory ops, IRQ notification races, incorrect PI-to-hardware matrix mapping, unsafe power-budget allocation, and disabled `CONFIG_PSE_CONTROLLER` callers mishandling `-EOPNOTSUPP`. Test ethtool netlink get/set paths, OF phandle lookup/refcounting, IRQ event mapping, static budget priority behavior, power limit range allocation/freeing, and no-PSE builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pse-pd/pse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pseudo_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/pseudo_fs.h

Purpose: declares the setup helper and context data for simple pseudo filesystems that need an internal superblock rather than a full mountable disk-backed filesystem.

Important APIs and types: `struct pseudo_fs_context` carries superblock operations, export operations, xattr handlers, dentry operations, magic number, and superblock dentry flags. `init_pseudo()` initializes an `fs_context` for a pseudo filesystem and returns the pseudo context.

Control flow: a pseudo filesystem init path calls `init_pseudo(fc, magic)`, fills or uses the returned context, and VFS mount/setup code consumes those operations to create a pseudo superblock.

State and persistence: state is per mount/context and superblock runtime metadata. Pseudo filesystems normally expose kernel objects and do not persist data.

Dependencies and integration points: depends on VFS `fs_context`, superblock, dentry, export, and xattr operation structures. Used by internal filesystems that need VFS semantics without backing storage.

Risks and test signals: risks include wrong magic values, missing operation callbacks for expected VFS behavior, and lifetime bugs in context allocation. Test mount/init failure paths, superblock teardown, xattr/dentry behavior, and export operation users if configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pseudo_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psi.h -->
# sources/distributed-fs/ceph-client/include/linux/psi.h

Purpose: declares Pressure Stall Information runtime APIs for system and cgroup pressure accounting, display, trigger creation/destruction, polling, and memory-stall annotations.

Important APIs and types: when `CONFIG_PSI` is enabled, `psi_disabled` and `psi_system` expose global state. APIs include `psi_init()`, `psi_memstall_enter()`, `psi_memstall_leave()`, `psi_show()`, `psi_trigger_create()`, `psi_trigger_destroy()`, and `psi_trigger_poll()`. Cgroup helpers include `cgroup_psi()`, `psi_cgroup_alloc()`, `psi_cgroup_free()`, `cgroup_move_task()`, and `psi_cgroup_restart()`. Disabled builds provide no-op init/stall hooks and direct cgroup pointer assignment.

Control flow: scheduler and reclaim paths annotate task pressure; memory reclaim sections call memstall enter/leave; procfs/cgroupfs display calls `psi_show()`; userspace-created triggers are polled through file/kernfs wait queues; cgroup task migration updates PSI group membership.

State and persistence: PSI maintains runtime per-system and per-cgroup pressure counters, averages, triggers, and wait queues. It is diagnostic/accounting state and does not persist across boot.

Dependencies and integration points: depends on jump labels, scheduler task state, cgroups, kernfs/proc seq files, polling, and `psi_types.h`. It integrates resource-pressure accounting with `/proc/pressure/*` and cgroup pressure files.

Risks and test signals: risks include hot-path overhead, incorrect cgroup migration accounting, memstall enter/leave imbalance, trigger lifetime races, and disabled-config semantic drift. Test pressure files, cgroup moves, trigger polling/rate limits, reclaim annotations, and builds with PSI or cgroups disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psi_types.h -->
# sources/distributed-fs/ceph-client/include/linux/psi_types.h

Purpose: defines the data model for Pressure Stall Information accounting: task-state counters, resource pressure states, per-CPU sampling buckets, trigger windows, and PSI group aggregation state.

Important APIs and types: `enum psi_task_count`, task bitmasks such as `TSK_IOWAIT` and `TSK_MEMSTALL`, `enum psi_res`, `enum psi_states`, `PSI_ONCPU`, and `PSI_STATE_RESCHEDULE` encode scheduler pressure. `struct psi_group_cpu` stores per-CPU task counts, state masks, times, and previous samples. `struct psi_window` tracks trigger windows. `struct psi_trigger` records threshold, state, event wait queue, kernfs file, rate limiting, and aggregator type. `struct psi_group` holds parent linkage, per-CPU data, averages, delayed work, average and RT-poll triggers, totals, and polling task/timer control.

Control flow: scheduler-side updates modify `psi_group_cpu` task counts and state masks; aggregator work samples per-CPU times into group totals and averages; triggers compare window growth against thresholds and wake waiters, with separate average and RT-poll aggregation paths.

State and persistence: all structures are runtime accounting state. Per-CPU fields are cacheline-separated for scheduler updates vs aggregation reads. Trigger lists and totals live per PSI group, usually system or cgroup.

Dependencies and integration points: depends on kthreads, timers, seqlock-related infrastructure, krefs, wait queues, cgroups through users, and scheduler clocks. It is consumed by `psi.h` implementation and cgroup/proc exposure.

Risks and test signals: risks include false sharing on hot scheduler fields, overflow/truncation in `u32 times`, trigger rate-limit mistakes, RT polling lifetime races, and state-mask bugs for full vs some pressure. Test per-resource pressure generation, cgroup hierarchy aggregation, trigger windows, RT polling activation/deactivation, IRQ accounting configs, and disabled `CONFIG_PSI` layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psi_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psp-platform-access.h -->
# sources/distributed-fs/ceph-client/include/linux/psp-platform-access.h

Purpose: declares AMD PSP platform-access mailbox APIs used by non-CCP drivers to communicate with platform firmware features such as firmware version queries, secure firmware services, HSTI, I2C requests, and dynamic boost parameters.

Important APIs and types: `enum psp_platform_access_msg` lists platform mailbox commands. `struct psp_req_buffer_hdr` and `struct psp_request` describe payload size/status and buffer pointer. APIs include `psp_send_platform_access_msg()`, `psp_ring_platform_doorbell()`, and `psp_check_platform_access_status()`.

Control flow: a client checks platform access status, prepares a request buffer with header and payload, sends a typed platform-access message, or rings a doorbell and reads the firmware result. The PSP driver serializes mailbox access and reports busy, timeout, absent-device, or I/O failures.

State and persistence: request state is transient; platform firmware may persist settings depending on message type. Mailbox recovery/busy state is owned by the PSP driver.

Dependencies and integration points: depends on `linux/psp.h`, AMD PSP/CCP driver binding, mailbox registers, and external platform feature drivers.

Risks and test signals: risks include wrong packed buffer layout, payload size mismatch, mailbox contention, timeout handling, and using the API before PSP platform features are ready. Test success and firmware error statuses, busy/recovery paths, timeout injection, absent PSP device, and each client message format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psp-platform-access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psp-sev.h -->
# sources/distributed-fs/ceph-client/include/linux/psp-sev.h

Purpose: defines the AMD Secure Encrypted Virtualization firmware command interface for SEV, SEV-ES, SEV-SNP, and newer TIO/platform features, including policy masks, command IDs, packed firmware command buffers, and exported PSP helper APIs.

Important APIs and types: policy masks cover SEV and SNP guest policy bits including SMT, migration agent, debug, single-socket, CXL, AES-256-XTS, RAPL disable, ciphertext hiding, and page-swap disable. `enum sev_state` and `enum sev_cmd` enumerate platform, guest, launch, migration, debug, SNP page/launch/config, firmware, feature, and TIO commands. Numerous `struct sev_data_*` packed buffers map exactly to firmware ABI command layouts, including launch start/update/finish, send/receive migration, attestation, SNP guest context/page operations, SNP init/shutdown/commit/feature info, and range lists. Exported helpers under `CONFIG_CRYPTO_DEV_SP_PSP` include `sev_module_init()`, `sev_platform_init()`, `sev_platform_status()`, `sev_issue_cmd_external_user()`, guest activate/deactivate/decommission/DF flush, `sev_do_cmd()`, `psp_copy_user_blob()`, SNP firmware page allocation/reclaim/free, shutdown, and SNP policy/feature queries.

Control flow: the PSP SEV driver initializes the platform, then KVM or userspace-facing code issues command-specific packed buffers through `sev_do_cmd()` or helper wrappers. Guest launch follows start, update data/VMSA or SNP page updates, measure/finish; migration follows send/receive sequences; SNP page lifecycle commands manage RMP-owned pages and firmware pages; external-user command issuance validates a SEV device file before forwarding a request.

State and persistence: state spans firmware platform state, guest handles/context pages, ASIDs, SNP RMP/page ownership, firmware NV storage, certificates, launch measurements, and driver-owned buffers. The header itself stores no state but defines ABI structures whose layout is persistent across firmware interfaces and sometimes across migrations.

Dependencies and integration points: depends on UAPI `psp-sev.h`, PSP/CCP crypto driver, x86 memory encryption physical address handling, KVM SEV/SNP code, firmware blobs, user file descriptors, and SNP RMP/page-management code.

Risks and test signals: risks are high: packed ABI drift, reserved bit misuse, physical address encryption conversion mistakes, firmware page leaks, SNP policy mismatch, page reclaim ordering bugs, command timeout/error propagation, and disabled-config callers expecting functionality. Test firmware command ABI sizes/layouts, SEV and SNP KVM launch/migration/attestation flows, platform init/shutdown, SNP page reclaim/free paths, feature-bit handling, user command validation, and `CONFIG_CRYPTO_DEV_SP_PSP=n` stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psp-sev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psp-tee.h -->
# sources/distributed-fs/ceph-client/include/linux/psp-tee.h

Purpose: declares the AMD PSP Trusted Execution Environment command interface used to communicate with AMD-TEE Trusted OS.

Important APIs and types: `enum tee_cmd_id` enumerates loading/unloading trusted applications, opening/closing sessions, invoking TA commands, and mapping/unmapping shared memory. `psp_tee_process_cmd()` submits a command buffer and returns a TEE status; `psp_check_tee_status()` checks whether a usable TEE exists. Disabled PSP builds return `-ENODEV`.

Control flow: the AMD TEE driver checks availability, prepares a command buffer for a TEE operation, calls `psp_tee_process_cmd()`, and reads the updated buffer/status on success. The PSP layer handles command submission and timeout/busy behavior.

State and persistence: session, TA, and shared-memory state is owned by the TEE/PSP implementation and Trusted OS. This header only defines the command IDs and call contract.

Dependencies and integration points: depends on PSP crypto device support, AMD TEE driver, shared memory mapping, and Trusted OS command ABI.

Risks and test signals: risks include invalid command buffer layout, stale shared memory mappings, session lifetime leaks, timeout/busy handling, and disabled-config behavior. Test TA load/session/invoke/unload cycles, map/unmap error paths, unavailable TEE, PSP reset/busy cases, and no-PSP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psp-tee.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psp.h -->
# sources/distributed-fs/ceph-client/include/linux/psp.h

Purpose: provides common AMD PSP mailbox bit definitions and physical-address conversion used by PSP-related subsystems.

Important APIs and types: `__psp_pa(x)` maps to `__sme_pa()` on x86 to account for SME memory encryption and to `__pa()` elsewhere. Bit masks define common command-response status, command, reserved, recovery, response, doorbell message, and ring bits, plus the TEE ring-busy status code.

Control flow: PSP clients construct mailbox command/response words using these masks and translate kernel virtual buffers to physical addresses with the correct encryption semantics before firmware access.

State and persistence: no state is stored. The definitions describe hardware register fields and address translation behavior.

Dependencies and integration points: depends on x86 memory encryption when applicable and generic physical address helpers. Used by PSP SEV, TEE, and platform-access code.

Risks and test signals: risks include using raw `__pa()` on encrypted x86 memory, interpreting command-response bits incorrectly for mailbox variants, and recovery bit mishandling. Test encrypted-memory platforms, mailbox command status decoding, and non-x86 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/psp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pstore.h -->
# sources/distributed-fs/ceph-client/include/linux/pstore.h

Purpose: defines the generic persistent storage backend interface used to save crash logs, console output, ftrace records, machine checks, and pmsg data into platform storage and expose them through pstorefs.

Important APIs and types: `enum pstore_type_id` defines ABI-sensitive record types. `struct pstore_record` carries record metadata, data buffer, ECC notice, backend private pointer, and dmesg-specific fields such as count/reason/part/compressed. `struct pstore_info` describes a backend with owner/name, crash dump buffer and raw spinlock, read mutex, frontend flags, max kmsg reason, private data, and callbacks `open`, `close`, `read`, `write`, `write_user`, and `erase`. Frontend flags include dmesg, console, ftrace, and pmsg. `pstore_register()` and `pstore_unregister()` manage backends. Ftrace helpers encode CPU either in IP or timestamp and store/read timestamp bits.

Control flow: a backend registers `pstore_info`; pstore core opens/read/closes it to enumerate records into pstorefs, calls `write()` from crash or frontend paths, optionally writes userspace pmsg data through `write_user()`, and erases records when pstorefs files are removed. Dmesg crash writes use the preallocated backend buffer because allocation may be unsafe after oops/panic.

State and persistence: backend storage is persistent across reboot by design. Runtime state includes preallocated buffers, callback serialization, record IDs, timestamps, ECC notices, and backend private record data freed by the core.

Dependencies and integration points: depends on kmsg dump reasons, pstorefs, console/ftrace/pmsg frontends, module ownership, mutex/spinlock primitives, and platform-specific backends such as EFI, ramoops, block, and zone.

Risks and test signals: risks include ABI record-type renumbering, crash-path allocation or locking, truncating compressed records, wrong erase identification, leaking `record->priv`, and ftrace CPU/timestamp encoding errors. Test panic/oops persistence, pstorefs read/erase, console/ftrace/pmsg frontends, ECC notices, backend unregister, and crash-time write constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pstore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pstore_blk.h -->
# sources/distributed-fs/ceph-client/include/linux/pstore_blk.h

Purpose: declares the pstore block-device backend interface and configuration structure built on top of pstore/zone.

Important APIs and types: `struct pstore_device_info` carries supported frontend flags and embedded `pstore_zone_info`. `register_pstore_device()` and `unregister_pstore_device()` manage a pstore block backend device. `struct pstore_blk_config` stores target device name, max kmsg reason, and per-frontend storage sizes. `pstore_blk_get_config()` returns the active configuration.

Control flow: a block-oriented backend fills zone operations and registers a `pstore_device_info`; pstore/blk code uses the zone layer to divide storage among kmsg, pmsg, console, and ftrace areas. Configuration can be queried by other code for diagnostics.

State and persistence: persistent records live on the configured block device/zone area. Runtime config records device name and partition sizes.

Dependencies and integration points: depends on pstore core and pstore_zone. It integrates block devices with persistent crash logging.

Risks and test signals: risks include mis-sized zones, wrong frontend flags, device path changes, and config query races during unregister. Test registration/unregistration, storage layout for each frontend size, block device removal, and config reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pstore_blk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pstore_ram.h -->
# sources/distributed-fs/ceph-client/include/linux/pstore_ram.h

Purpose: defines platform data for the ramoops persistent RAM pstore backend, including reserved memory layout and ECC configuration.

Important APIs and types: `struct persistent_ram_ecc_info` describes ECC block size, ECC size, symbol size, polynomial, and parity buffer. `RAMOOPS_FLAG_FTRACE_PER_CPU` configures per-CPU ftrace areas. `struct ramoops_platform_data` carries reserved memory size/address/type, record/console/ftrace/pmsg sizes, max dump reason, flags, and ECC info.

Control flow: platform code supplies `ramoops_platform_data` to the ramoops driver; the driver maps reserved RAM, divides it into frontend areas, applies ECC configuration, and registers with pstore.

State and persistence: reserved RAM contents persist across warm reboot if the platform preserves memory. Runtime platform data defines the layout used to interpret that memory.

Dependencies and integration points: depends on pstore core, persistent RAM backend implementation, reserved memory, platform data or equivalent firmware descriptions, and ECC support.

Risks and test signals: risks include reserved memory overlap, size misalignment, ECC parameter mismatch, losing records on memory clearing, and incorrect per-CPU ftrace partitioning. Test boot with reserved memory, panic persistence, ECC correction notices, per-frontend sizing, and reboot record recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pstore_ram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pstore_zone.h -->
# sources/distributed-fs/ceph-client/include/linux/pstore_zone.h

Purpose: declares the generic zoned pstore backend abstraction used by block and similar storage devices to expose read/write/erase/panic-write operations over fixed storage regions.

Important APIs and types: operation typedefs define read, write, and erase signatures using buffer, size, and storage-relative offset. `struct pstore_zone_info` carries module owner, backend name, total size, per-frontend zone sizes, max kmsg reason, regular read/write/erase callbacks, and optional `panic_write`. `register_pstore_zone()` and `unregister_pstore_zone()` manage the backend.

Control flow: a zone backend registers total and per-frontend sizes plus callbacks. Pstore/zone uses relative offsets to read/write records, retries on `-EBUSY`, advances zones on `-ENOMSG`, and can call `panic_write()` in panic contexts if provided.

State and persistence: persistent state is in the backing zone storage. Runtime state is the registered zone descriptor and backend device state.

Dependencies and integration points: integrates pstore core/frontends with block-like or MTD-like storage backends. Depends on module ownership and low-level storage drivers.

Risks and test signals: risks include violating required 4 KiB/sector-size multiples, panic-write using unsafe paths, offset arithmetic bugs, and wrong handling of `-EBUSY`/`-ENOMSG`. Test size validation, panic and normal writes, erase, backend removal, and multi-zone rollover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pstore_zone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptdump.h -->
# sources/distributed-fs/ceph-client/include/linux/ptdump.h

Purpose: declares generic page-table dump walking hooks used for debugfs/proc-style page table inspection and W+X permission checks.

Important APIs and types: `struct ptdump_range` describes address ranges. `struct ptdump_state` carries callbacks for each page table level, flush notification, effective protection aggregation, and a range list. APIs include `ptdump_walk_pgd_level_core()`, `ptdump_walk_pgd()`, `ptdump_check_wx()`, and inline `debug_checkwx()`.

Control flow: architecture or debug code initializes a `ptdump_state` and walks a PGD for an `mm_struct`; callbacks observe PTE/PMD/PUD/P4D/PGD entries and effective protections. `debug_checkwx()` conditionally checks for writable-executable mappings when `CONFIG_DEBUG_WX` is enabled.

State and persistence: no state is stored here; walkers inspect live page tables. Dump output and check results are transient diagnostics.

Dependencies and integration points: depends on MM page table types, seq_file users, architecture page table formats, and debug W+X checking.

Risks and test signals: risks include walking unstable page tables without proper locking, incorrect effective-protection aggregation, missing folded levels, and false W+X reports. Test kernel page table dumps across paging modes, DEBUG_WX boot checks, huge mappings, folded-level architectures, and user/kernel mm walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptdump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pti.h -->
# sources/distributed-fs/ceph-client/include/linux/pti.h

Purpose: provides a generic include wrapper for Page Table Isolation initialization and finalization.

Important APIs and types: with `CONFIG_MITIGATION_PAGE_TABLE_ISOLATION`, it includes architecture `asm/pti.h`; otherwise `pti_init()` and `pti_finalize()` are empty inline stubs.

Control flow: architecture/init code can call `pti_init()` early and `pti_finalize()` later without open-coding config guards. Enabled builds dispatch to arch-specific PTI setup.

State and persistence: no state is defined here; enabled architectures maintain PTI page table and mitigation state.

Dependencies and integration points: depends on architecture PTI implementation and mitigation config. It integrates boot-time CPU vulnerability mitigation with generic init code.

Risks and test signals: risks include init ordering bugs, disabled stubs masking missing mitigation, and architecture header drift. Test PTI-enabled and disabled boot paths, CPU vulnerability reporting, and page table isolation correctness under syscall/interrupt transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pti.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptp_classify.h -->
# sources/distributed-fs/ceph-client/include/linux/ptp_classify.h

Purpose: defines PTP packet classification constants, PTP header layouts, and helpers for recognizing and modifying IEEE 1588 event messages in networking paths.

Important APIs and types: `PTP_CLASS_*` flags classify protocol version and transport: IPv4, IPv6, L2, VLAN, and none. Message constants cover Sync, Delay_Req, Pdelay_Req, and Pdelay_Resp. `struct clock_identity`, `struct port_identity`, and packed `struct ptp_header` model PTPv2 headers. With `CONFIG_NET_PTP_CLASSIFY`, APIs include `ptp_classify_raw()`, `ptp_parse_header()`, `ptp_get_msgtype()`, `ptp_header_update_correction()`, `ptp_msg_is_sync()`, and `ptp_classifier_init()`.

Control flow: network drivers or timestamping code classify an skb, parse the PTP header accounting for VLAN/UDP/IP headers, inspect message type, and for one-step P2P correction update the correction field and UDP checksum. Disabled builds return no classification and no-op helpers.

State and persistence: no persistent state. Classification operates on live skbs and may mutate the PTP correction field and UDP checksum in packet data.

Dependencies and integration points: depends on skb layout, MAC headers, IP/UDP headers, unaligned access, checksum helpers, BPF-based classifier implementation, and hardware timestamping drivers.

Risks and test signals: risks include parsing with uninitialized skb MAC headers, length checks missing encapsulation variants, checksum update errors, PTPv1/v2 message-type differences, and VLAN handling. Test raw classification for IPv4/IPv6/L2/VLAN PTP, malformed/truncated packets, UDP checksum zero/mangled-zero behavior, correction update, and disabled classifier builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptp_classify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptp_clock_kernel.h -->
# sources/distributed-fs/ceph-client/include/linux/ptp_clock_kernel.h

Purpose: declares the in-kernel PTP Hardware Clock provider/consumer interface, including clock registration, driver operation callbacks, event notification, auxiliary work, timestamp cross-sampling helpers, virtual clock conversion, and scaled-ppm arithmetic.

Important APIs and types: `struct ptp_clock_request` describes EXTS, PEROUT, and PPS requests. `struct ptp_system_timestamp` carries pre/post system timestamps and clock ID. `struct ptp_clock_info` is the driver callback table for frequency/phase/time adjustment, time/cycle reads, cross timestamps, feature enable, pin verification, auxiliary work, and perout loopback. `struct ptp_clock_event` reports alarm, external timestamp, offset, PPS, and user PPS events. Helpers include `scaled_ppm_to_ppb()`, `diff_by_scaled_ppm()`, and `adjust_by_scaled_ppm()`. Public APIs include `ptp_clock_register()`, `ptp_clock_unregister()`, `ptp_clock_event()`, `ptp_clock_index()`, index lookup by OF node or parent device, `ptp_find_pin*()`, worker scheduling/cancel, built-in-only virtual clock index lookup/conversion, and pre/post system timestamp readers.

Control flow: a PHC driver fills `ptp_clock_info`, registers it, responds to core ioctl/sysfs requests through callbacks, reports timestamp/PPS events with `ptp_clock_event()`, and unregisters on removal. Consumers may resolve a PHC index by device, find pin mappings under core locking, schedule auxiliary driver work, or convert timestamps to virtual PHC time when PTP is built in.

State and persistence: runtime state is owned by the PTP core and driver: registered clocks, pin configuration, event queues, auxiliary work, and hardware time. PHC time is hardware state and may persist depending on device power.

Dependencies and integration points: depends on device model, PPS, PTP UAPI, timecounter/timekeeping, skbuff timestamping, OF nodes, kthread work, and network timestamp consumers. It is the core bridge between NIC/PHC drivers and userspace `/dev/ptp*`.

Risks and test signals: risks include callback sleeping/atomic-context mismatch, bad `max_adj`, deprecated `gettime64` use, inconsistent cross timestamp windows, pin mux races, unsupported flag handling, arithmetic overflow in frequency adjustment, and module vs built-in virtual clock restrictions. Test PHC registration/removal, ioctl adjustment/set/get, external timestamp and PPS events, pin assignment validation, aux worker lifecycle, virtual clock conversion, and `CONFIG_PTP_1588_CLOCK` disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptp_clock_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptp_kvm.h -->
# sources/distributed-fs/ceph-client/include/linux/ptp_kvm.h

Purpose: declares architecture hooks for the virtual PTP clock used by KVM guests to obtain host-synchronized time.

Important APIs and types: `kvm_arch_ptp_init()` and `kvm_arch_ptp_exit()` manage arch-specific setup. `kvm_arch_ptp_get_clock()` returns a `timespec64` clock value. `kvm_arch_ptp_get_crosststamp()` returns cycle, timespec, and clocksource ID for cross timestamping.

Control flow: the KVM PTP driver initializes arch support, services guest/PHC clock reads through arch hooks, optionally obtains cross timestamps, then tears down on exit.

State and persistence: state is architecture/KVM runtime state and host timekeeping state. No persistent data is defined here.

Dependencies and integration points: depends on KVM paravirtual time, clocksource IDs, timekeeping, and architecture implementations. It integrates guest-visible PTP devices with host clocks.

Risks and test signals: risks include time discontinuities, wrong clocksource IDs, cross timestamp inconsistency, and init/exit ordering with KVM modules. Test guest PTP reads, host time steps, live migration/time sync behavior, and arch-specific failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptp_kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptp_mock.h -->
# sources/distributed-fs/ceph-client/include/linux/ptp_mock.h

Purpose: declares a mock PTP Hardware Clock helper for virtual network devices and tests that need a PHC index without real hardware.

Important APIs and types: opaque `struct mock_phc` is created with `mock_phc_create()`, destroyed with `mock_phc_destroy()`, and queried for its PHC index with `mock_phc_index()`. Disabled builds return `NULL` and `-1`.

Control flow: a virtual driver creates a mock PHC during device setup, exposes or uses its index for timestamping paths, and destroys it during teardown.

State and persistence: mock clock state is runtime-only and tied to the parent device lifetime.

Dependencies and integration points: depends on `CONFIG_PTP_1588_CLOCK_MOCK`, device model, and PTP clock core. Integrates virtual network devices with timestamping tests or features.

Risks and test signals: risks include leaking mock PHCs on device removal, using `-1` indexes when config is disabled, and diverging behavior from real PHCs. Test create/destroy cycles, index visibility, virtual device teardown, and disabled config fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptp_mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptp_pch.h -->
# sources/distributed-fs/ceph-client/include/linux/ptp_pch.h

Purpose: declares helper accessors for the PCH PTP hardware block behind PCI devices.

Important APIs and types: functions write channel control and event registers, read source UUID low/high words, read RX/TX snapshot timestamps, and set station address for a `pci_dev`.

Control flow: a PCH PTP or network driver calls these helpers to configure timestamp channels, clear/read events, retrieve captured timestamps, and program the station address used by hardware timestamping.

State and persistence: state is hardware register state in the PCI device. Snapshot registers reflect transient packet timestamp events.

Dependencies and integration points: depends on PCI device access and PCH-specific PTP hardware. Integrates timestamp capture with network drivers on affected platforms.

Risks and test signals: risks include register ordering, stale event bits, endianness/width issues reading 64-bit snapshots, and invalid station address programming. Test TX/RX timestamp capture, event clear/write behavior, UUID reads, PCI remove/suspend, and station address updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptp_pch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptr_ring.h -->
# sources/distributed-fs/ceph-client/include/linux/ptr_ring.h

Purpose: implements an inline fixed-size FIFO ring of pointers optimized for one producer CPU and one consumer CPU, with lock variants for normal, IRQ, IRQ-save, and BH contexts plus resize/unconsume helpers.

Important APIs and types: `struct ptr_ring` stores producer index/lock, consumer head/tail/lock, size, batch threshold, and pointer queue. APIs include full/empty tests, `__ptr_ring_produce()` and locked produce variants, peek/consume/discard/batched consume variants, peek-call macros, queue allocation/init, `ptr_ring_unconsume()`, resize helpers, multi-ring BH resize, and cleanup with optional destroy callback.

Control flow: producer acquires producer lock, checks current producer slot for fullness, executes `smp_wmb()`, writes the pointer, and advances/wraps. Consumer acquires consumer lock, reads the head with `READ_ONCE()`, processes dependency-ordered pointer data, batches slot zeroing through consumer tail to reduce cache contention, and advances head. Resize nests producer lock inside consumer lock, drains old queue into a new queue, destroys overflow entries, swaps queues, and frees old memory.

State and persistence: all queue state is in memory. Entries remain owned by callers until consumed or destroyed. `consumer_tail` defers invalidation, so occupied slots can lag logical consumption for batching.

Dependencies and integration points: depends on spinlocks, cacheline alignment, memory barriers, kvmalloc/kvfree, allocation hooks, and caller-provided pointer lifetime rules. It is used by high-throughput producer/consumer paths such as networking and virtio-like queues.

Risks and test signals: risks include wrong lock nesting during resize, using lockless empty/full checks while resizing, missing compiler barriers in polling loops, producer writing invalid pointers before `smp_wmb()`, destroy callback omissions, and interrupt/BH context mismatches. Test SPSC produce/consume order, full/empty transitions, batched consume wraparound, unconsume overflow destruction, resize under load, KCSAN/lockdep, and IRQ/BH variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptr_ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptrace.h -->
# sources/distributed-fs/ceph-client/include/linux/ptrace.h

Purpose: defines the generic in-kernel ptrace control surface: tracing flags, permission checks, task link/unlink helpers, event notification, syscall tracing reports, single-step/block-step arch hooks, and process memory access helpers.

Important APIs and types: `struct syscall_info` extends `seccomp_data` with stack pointer. Flags include `PT_PTRACED`, `PT_SEIZED`, trace event enables, `PT_EXITKILL`, and `PT_SUSPEND_SECCOMP`. Permission modes include read/attach and fscreds/realcreds combinations. APIs include `ptrace_access_vm()`, `arch_ptrace()`, data read/write helpers, `ptrace_disable()`, `ptrace_request()`, `ptrace_notify()`, link/unlink/exit helpers, `ptrace_may_access()`, generic peek/poke, `task_current_syscall()`, and compat sigaction ABI handling. Inline helpers cover `ptrace_parent()`, `ptrace_event_enabled()`, `ptrace_event()`, `ptrace_event_pid()`, `ptrace_init_task()`, `ptrace_release_task()`, syscall success handling, arch single-step fallbacks, `user_single_step_report()`, and syscall entry/exit reports.

Control flow: fork initializes ptrace fields and optionally links a traced child to the parent's tracer; event sites check enabled bits and call `ptrace_notify()`; syscall entry/exit work reports traps and may abort syscall entry; reaping releases ptrace links. Architecture code supplies request handling and stepping behavior where supported.

State and persistence: ptrace state lives in `task_struct`: flags, parent/real_parent relationships, ptraced lists, jobctl, pending signals, and ptracer credentials. It is runtime process-control state and ends with task lifetime.

Dependencies and integration points: depends on scheduler/task structures, signal delivery, pid namespaces, seccomp, credentials, UAPI ptrace constants, architecture register/syscall helpers, and process_vm-style memory access. It is a security-sensitive interface between debuggers/tracers and traced tasks.

Risks and test signals: risks include credential mode mistakes, ptrace parent namespace races in `ptrace_event_pid()`, signal/jobctl state bugs, single-step fallback misuse, syscall abort semantics, memory access permission bypass, and tasklist/RCU lifetime errors. Test ptrace attach/seize, fork/vfork/clone/exec/exit/seccomp events, pid namespaces, syscall tracing and emulation, single-step/block-step per architecture, process memory read/write, and LSM/Yama-style permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptrace_api.h -->
# sources/distributed-fs/ceph-client/include/linux/ptrace_api.h

Purpose: provides a compatibility include shim that simply includes `linux/ptrace.h`.

Important APIs and types: no new APIs or types are defined; all functionality is inherited from `ptrace.h`.

Control flow: code including this header receives the generic ptrace declarations.

State and persistence: none.

Dependencies and integration points: depends entirely on `linux/ptrace.h`. It exists for include compatibility with code expecting `ptrace_api.h`.

Risks and test signals: risks are limited to include-cycle or stale compatibility expectations. Test by building users that include `ptrace_api.h` directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ptrace_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/purgatory.h -->
# sources/distributed-fs/ceph-client/include/linux/purgatory.h

Purpose: declares global purgatory symbols used by kexec to verify loaded segments before jumping to a new kernel.

Important APIs and types: `struct kexec_sha_region` describes a memory range with start and length. `purgatory_sha_regions[KEXEC_SEGMENT_MAX]` and `purgatory_sha256_digest[SHA256_DIGEST_SIZE]` are externally visible symbols required for kexec symbol lookup and sparse checking.

Control flow: kexec code populates SHA regions and expected digest in the purgatory image; purgatory code computes/verifies the digest before transfer to the next kernel.

State and persistence: the arrays are part of the loaded purgatory/kexec image state for a pending kexec operation. They do not persist beyond boot transition.

Dependencies and integration points: depends on crypto SHA-256 constants and UAPI kexec segment limits. Integrates generic kexec loading with architecture purgatory code.

Risks and test signals: risks include symbol visibility changes breaking kexec relocation, wrong segment count/lengths, digest mismatch handling, and sparse/build drift in arch purgatory. Test kexec load/execute, corrupted segment detection, max segment counts, and architecture purgatory builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/purgatory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pvclock_gtod.h -->
# sources/distributed-fs/ceph-client/include/linux/pvclock_gtod.h

Purpose: declares notifier registration for paravirtual clock users that need to track system time-of-day updates.

Important APIs and types: `pvclock_gtod_register_notifier()` and `pvclock_gtod_unregister_notifier()` manage a `notifier_block`. Notifier actions indicate whether system time was stepped.

Control flow: a paravirtual clock provider registers a notifier, receives callbacks when system time is updated, and updates guest-visible time synchronization data; it unregisters during teardown.

State and persistence: state is the notifier chain and registered blocks in memory. Guest time synchronization state is maintained by notifier users.

Dependencies and integration points: depends on Linux notifier infrastructure and timekeeping update paths. Integrates KVM/paravirtual clock code with host time changes.

Risks and test signals: risks include notifier leaks, callback ordering, handling stepped vs slewed time incorrectly, and teardown races. Test register/unregister, host time step events, concurrent callbacks during module removal, and guest time monotonicity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pvclock_gtod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pwm.h -->
# sources/distributed-fs/ceph-client/include/linux/pwm.h

Purpose: defines the PWM framework's consumer and provider API, including PWM state, waveform representation, chip registration, apply/capture operations, lookup tables, device-tree translation, and config-disabled stubs.

Important APIs and types: `enum pwm_polarity`, `struct pwm_args`, `struct pwm_waveform`, `struct pwm_state`, `struct pwm_device`, `struct pwm_capture`, `struct pwm_ops`, `struct pwm_chip`, and `struct pwm_lookup` form the core model. Consumer helpers read/init state, get/set relative duty cycle, round/get/set waveform, apply state in sleeping or atomic context, get hardware state, adjust config, legacy config/enable/disable, and get/put PWM devices. Provider APIs allocate/register/remove chips, support devm registration, translate OF specifiers, expose chip driver data, and manage lookup tables.

Control flow: providers allocate a `pwm_chip`, fill ops, register it, and the framework creates per-channel `pwm_device` objects. Consumers obtain a PWM by device/connection, initialize state from board args, modify duty/period/polarity/enabled fields, and call `pwm_apply_might_sleep()` or `pwm_apply_atomic()` depending on chip atomic capability. Waveform callbacks provide a more expressive offset-aware representation when supported.

State and persistence: PWM framework state includes chip device/cdev, per-channel flags, args, last applied state, optional debug last implemented state, operational flag, locks, and lookup tables. Hardware PWM state may persist through consumer lifetime or hardware reset.

Dependencies and integration points: depends on device model, cdev, GPIO integration, OF/fwnode lookup, modules, mutex/spinlock, and driver callbacks. It integrates backlight, LED, regulator-like, motor, fan, and SoC PWM controller users.

Risks and test signals: risks include applying invalid duty > period, using sleeping apply in atomic context, provider `atomic` flag mismatch, waveform conversion inconsistencies, chip removal while consumers hold devices, lookup table module ownership, and disabled `CONFIG_PWM` stubs returning different errors. Test consumer get/apply/put, atomic vs might-sleep paths, provider registration/removal, OF lookup, waveform exact/rounded paths, relative duty helpers, capture timeouts, and no-PWM builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pwm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pwm_backlight.h -->
# sources/distributed-fs/ceph-client/include/linux/pwm_backlight.h

Purpose: defines platform data for the generic PWM backlight driver.

Important APIs and types: `struct platform_pwm_backlight_data` carries max/default/low-threshold brightness, PWM period, optional brightness levels table, on/off delays, and callbacks for init, brightness notify, post-notify, and exit.

Control flow: board/platform code supplies this data to the PWM backlight driver; the driver initializes hardware, maps brightness through levels or linear range, applies PWM duty, calls notify hooks around changes, and delays around power transitions.

State and persistence: platform data is static configuration. Runtime brightness and PWM state are managed by the backlight driver and PWM framework.

Dependencies and integration points: depends on backlight subsystem and PWM consumer API. Integrates board-specific panel/backlight sequencing with the generic driver.

Risks and test signals: risks include invalid brightness defaults, level table lifetime, wrong PWM period units, callback failures, and delay ordering causing panel artifacts. Test brightness changes, suspend/resume, init/exit hooks, notify transformations, and level-table mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pwm_backlight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pwrseq/consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/pwrseq/consumer.h

Purpose: declares the consumer-side API for generic power sequencing targets.

Important APIs and types: opaque `struct pwrseq_desc` represents an acquired sequence target. APIs include `pwrseq_get()`, `pwrseq_put()`, `devm_pwrseq_get()`, `pwrseq_power_on()`, and `pwrseq_power_off()`. Disabled builds return `ERR_PTR(-ENOSYS)` or `-ENOSYS`.

Control flow: a device driver gets a sequencer descriptor for a named target, powers it on before using dependent hardware, powers it off during teardown or suspend, and releases the descriptor manually or through devm.

State and persistence: descriptor and unit state are owned by the power sequencing core/provider. Power state affects hardware rails/resets/clocks but is runtime state.

Dependencies and integration points: depends on device model, provider matching, and the power sequencing core. Integrates consumers with shared ordered power-up/down sequences.

Risks and test signals: risks include ignoring `ERR_PTR`, unbalanced on/off calls, target name mismatch, and disabled-config behavior. Test get/put lifetime, devm cleanup, shared consumers, power-on/off ordering, and no-power-sequencing builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pwrseq/consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pwrseq/provider.h -->
# sources/distributed-fs/ceph-client/include/linux/pwrseq/provider.h

Purpose: declares the provider-side API and data model for registering reusable power sequencers composed of dependency-ordered units and named targets.

Important APIs and types: callback typedefs are `pwrseq_power_state_func` and `pwrseq_match_func`; match results are `PWRSEQ_NO_MATCH` and `PWRSEQ_MATCH_OK`. `struct pwrseq_unit_data` describes a named unit, its NULL-terminated dependencies, and enable/disable callbacks. `struct pwrseq_target_data` names a target, final required unit, and optional post-enable callback run after the state lock is released. `struct pwrseq_config` supplies parent device, owner, driver data, match callback, and NULL-terminated targets. APIs register/unregister providers, devm-register providers, and retrieve driver data.

Control flow: a provider defines units and dependency graph, defines targets, registers a `pwrseq_device`, and matches consumers by device. The core enables dependencies before a target unit, disables in reverse dependency order, and can run post-enable delays outside the state lock.

State and persistence: provider state includes registered sequencer device, target/unit state, dependencies, module ownership, and driver data. Hardware side effects are runtime power/reset state.

Dependencies and integration points: depends on device model, modules, consumer API, and provider drivers for regulators, GPIOs, clocks, resets, or board-specific sequencing.

Risks and test signals: risks include cyclic or unterminated dependency arrays, post-enable races after lock release, provider removal with active consumers, and incorrect match decisions. Test dependency ordering, shared targets, provider unregister under references, post-enable delays, devm cleanup, and failure rollback when a unit enable fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pwrseq/provider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pxa168_eth.h -->
# sources/distributed-fs/ceph-client/include/linux/pxa168_eth.h

Purpose: defines platform data for the Marvell/PXA168 Ethernet driver.

Important APIs and types: `struct pxa168_eth_platform_data` carries port number, PHY address, optional fixed speed and duplex, PHY interface mode, optional RX/TX queue sizes, and a board-specific init callback.

Control flow: board code provides platform data; the Ethernet driver uses it to select port/PHY/interface, choose autonegotiation or fixed link settings, size queues, and run board initialization such as PHY transceiver setup.

State and persistence: platform data is static boot-time configuration. Link state, queues, and PHY state are runtime driver/hardware state.

Dependencies and integration points: depends on PHY constants and the PXA168 Ethernet platform driver. Integrates board files with network device initialization.

Risks and test signals: risks include invalid PHY address, mismatched fixed speed/duplex, wrong interface mode, queue size extremes, and init callback failures. Test autonegotiated and fixed-link modes, PHY init, queue sizing, and platform remove/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pxa168_eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pxa2xx_ssp.h -->
# sources/distributed-fs/ceph-client/include/linux/pxa2xx_ssp.h

Purpose: defines register offsets, bit fields, controller type IDs, device state, and helper APIs for PXA2xx-family SSP/SPI/I2S-style serial ports and related Intel variants.

Important APIs and types: macros cover SSCR/SSSR/SSPSP/SST*/SSACD register offsets and bit fields for PXA25x/PXA27x/PXA3xx, CE4100, Quark X1000, Merrifield, LPSS, and LPT/WPT variants. `enum pxa_ssp_type` identifies controller variants. `struct ssp_device` stores device, list node, clock, MMIO base, physical base, label, port ID, type, use count, IRQ, and OF node. Inline helpers read/write raw registers and enable/disable SSE. APIs under `CONFIG_PXA_SSP` request/free by port or OF node.

Control flow: a client requests an SSP device, programs registers through read/write helpers and bit macros, enables the port, performs transfers through higher-level SPI/serial code, disables when idle, and frees the device. Controller-specific macros select correct FIFO thresholds and data-size fields.

State and persistence: state includes hardware registers, clock enablement, use count, list membership, and MMIO mapping. Register state is hardware runtime state and may reset on suspend or power loss.

Dependencies and integration points: depends on IO accessors, clocks, device/OF model, SPI/SSP platform code, and SoC-specific register layouts. It integrates legacy PXA and Intel SSP controllers with serial/SPI/audio drivers.

Risks and test signals: risks include using wrong variant bit masks, raw MMIO ordering assumptions, unbalanced request/free use counts, enabling before clock/config, FIFO threshold mismatches, and disabled-config callers getting `NULL`. Test probe/request by port and OF, register programming for each supported variant, enable/disable sequencing, suspend/resume restore, SPI transfers, and error paths for busy ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pxa2xx_ssp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qat/qat_mig_dev.h -->
# sources/distributed-fs/ceph-client/include/linux/qat/qat_mig_dev.h

Purpose: declares the Intel QuickAssist Technology virtual-function migration device interface used to save, transfer, and restore VF state.

Important APIs and types: `struct qat_mig_dev` stores parent accelerator device pointer, migration state buffer, setup and remote setup sizes, state size, and VF ID. Lifecycle and migration APIs include create, init, cleanup, reset, open, close, suspend, resume, save state, save setup, load state, load setup, and destroy.

Control flow: a migration-capable QAT VF path creates and initializes a migration device for a PCI VF, opens it for migration, suspends the VF, saves setup/state into buffers, transfers them externally, loads remote setup/state on the target, resumes, then closes and destroys/cleans up.

State and persistence: migration buffers hold device setup and runtime state snapshots. The state is transient during migration but represents hardware/VF state that must be faithfully restored on the destination.

Dependencies and integration points: depends on PCI devices and QAT accelerator driver internals. It integrates QAT VFIO/live-migration flows with hardware-specific state capture.

Risks and test signals: risks include buffer size mismatches between source and destination, stale state after reset, VF ID mismatch, open/close imbalance, suspend/resume ordering bugs, and partial load failures. Test same-version and cross-version migration setup sizes, suspend/save/resume cycles, reset handling, target load failures, and cleanup after interrupted migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qat/qat_mig_dev.h -->
