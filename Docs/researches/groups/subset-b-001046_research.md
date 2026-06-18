# subset-b-001046 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/cpu.c -->
## sources/distributed-fs/ceph-client/drivers/base/cpu.c

### Purpose
`cpu.c` implements the driver-core CPU subsystem and the `/sys/devices/system/cpu` surface. It registers per-CPU devices, exposes CPU masks and CPU vulnerability attributes, supports hotplug online/offline operations, and provides helper device creation under CPU devices.

### Important APIs, Types, And Functions
Important state includes per-CPU `cpu_sys_devices`, `cpu_subsys`, `total_cpus`, and optional per-CPU `cpu_devices`. Key APIs are `register_cpu()`, `unregister_cpu()`, `get_cpu_device()`, `cpu_device_create()`, `cpu_is_hotpluggable()`, weak `arch_register_cpu()` and `arch_unregister_cpu()`, and `cpu_dev_init()`. Sysfs helpers print online, possible, present, offline, enabled, isolated, housekeeping, nohz_full, crash, modalias, and vulnerability data.

### Control Flow, State, And Persistence
`cpu_dev_init()` registers the CPU bus with root attributes, registers present CPUs when generic CPU devices are enabled, then installs vulnerability attributes. `register_cpu()` initializes a `struct cpu` device, binds it to `cpu_subsys`, registers it in sysfs, records it in the per-CPU pointer array, links it under its NUMA node, exposes resume latency QoS, and marks it enabled. Hotplug online retries transient `-EBUSY`, then adjusts NUMA node links if CPU-to-node mapping changed.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on ACPI matching, OF CPU nodes, NUMA node devices, CPU hotplug, cpumasks, scheduler isolation, tick/nohz, crash dump notes, PM QoS, and architecture hooks. Risks center on hotplug races, static CPU device lifetime, sysfs output staying within page buffers, weak fallback vulnerability text hiding architecture omissions, and NUMA relinking. Test signals include CPU online/offline sysfs operations, node relink after memoryless-node hot add, cpumask output, crash note addresses, modalias generation, and vulnerability group registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/dd.c -->
## sources/distributed-fs/ceph-client/drivers/base/dd.c

### Purpose
`dd.c` owns core driver/device binding and unbinding. It handles deferred probe, async probing, driver override, sysfs bind links, coredump hooks, device links, PM ordering, and cleanup after failed or successful probe/remove paths.

### Important APIs, Types, And Functions
Important exported APIs include `driver_deferred_probe_add()`, `driver_deferred_probe_del()`, `driver_deferred_probe_trigger()`, `device_block_probing()`, `device_unblock_probing()`, `driver_deferred_probe_check_state()`, `device_bind_driver()`, `wait_for_device_probe()`, `device_attach()`, `device_initial_probe()`, `device_driver_attach()`, `driver_attach()`, `device_release_driver()`, `device_driver_detach()`, and `driver_detach()`. State includes deferred pending/active lists, `deferred_probe_work`, `deferred_trigger_count`, `initcalls_done`, `defer_all_probes`, async probe command-line state, and `probe_count`.

### Control Flow, State, And Persistence
Probe moves through match, runtime-PM supplier/parent get, supplier link checks, `device_set_driver()`, pinctrl/DMA setup, sysfs link creation, PM-domain activation, bus or driver probe, driver groups, optional `state_synced`, and final `driver_bound()`. Probe errors unwind sysfs, DMA, links, devres, PM domain, driver data, and runtime PM. Deferred probes are queued on pending lists, promoted to active on successful binds, and retried by workqueue; initcall timeout forces final retries and warnings. Unbind removes sysfs links, notifies bus, runs remove callbacks, releases devres, tears down DMA/PM, removes driver klist membership, and sends uevents.

### Dependencies, Integration Points, Risks, And Test Signals
This file integrates buses, drivers, device links, fw_devlink, runtime PM, pinctrl, DMA ops, PM domains, debugfs, async core, kobjects, and devcoredump. Risks include lock ordering with parent locks, asynchronous probe races, deferred trigger races, positive-vs-negative probe errno conventions, cleanup ordering, and deadlock if remove recursively releases its own device. Test signals include deferred probe timeout behavior, async-probe command line, supplier link deferral, failed probe unwind, bind/unbind uevents and links, `CONFIG_DEBUG_TEST_DRIVER_REMOVE`, and suspend-safe probe blocking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/dd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/devcoredump.c -->
## sources/distributed-fs/ceph-client/drivers/base/devcoredump.c

### Purpose
`devcoredump.c` implements `/sys/class/devcoredump`, allowing drivers to publish temporary crash dumps for failed devices. It supports vmalloc buffers, scatterlist dumps, custom read/free callbacks, timeout-based cleanup, manual deletion, and a global security disable knob.

### Important APIs, Types, And Functions
`struct devcd_entry` wraps the class device, dump data, callbacks, owner module, failing device reference, deletion work, and race-protection mutex flags. Public APIs are `dev_coredumpv()`, `dev_coredumpsg()`, `dev_coredumpm_timeout()`, and `dev_coredump_put()`. Sysfs exposes binary `data` and class attribute `disabled`.

### Control Flow, State, And Persistence
Creation rejects dumps when disabled or when a dump already exists for the failing device, pins the callback module, initializes a `devcd` device, schedules deletion before `device_add()`, links to the failing device, enables uevents, and marks initialization complete. Reading dispatches through the stored read callback; writing to `data` schedules immediate deletion. The delayed worker, disable path, and explicit put converge on `devcd_free()` and `__devcd_del()`, with `deleted` preventing double destruction. Release frees data, drops module and failing device references, removes links, and frees the entry.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the device class core, sysfs binary attributes, workqueues, module refs, scatterlist copy helpers, vmalloc, and failing-device kobjects. Risks are lifetime races between device creation and deletion, disable-vs-worker concurrency, one-dump-per-device policy discarding later dumps, and careful ownership transfer of caller data. Test signals include duplicate dump suppression, read/write delete, timeout expiry, disabled write-once behavior, sgtable reads with offsets, module unload using `dev_coredump_put()`, and link cleanup after failing device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/devcoredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/devres.c -->
## sources/distributed-fs/ceph-client/drivers/base/devres.c

### Purpose
`devres.c` implements device-managed resource lifetime. It lets drivers allocate resources, attach release callbacks to devices, group resource acquisitions, install custom teardown actions, and use managed kmalloc/pages/percpu helpers that unwind automatically on driver detach.

### Important APIs, Types, And Functions
Core types are `struct devres`, `struct devres_group`, `struct devres_node`, `struct devres_action`, and `struct pages_devres`. Major APIs include `__devres_alloc_node()`, `devres_add()`, `devres_find()`, `devres_get()`, `devres_remove()`, `devres_destroy()`, `devres_release()`, `devres_release_all()`, `devres_open_group()`, `devres_close_group()`, `devres_remove_group()`, `devres_release_group()`, `__devm_add_action()`, `devm_release_action()`, `devm_kmalloc()`, `devm_krealloc()`, string/memdup helpers, managed pages, and managed percpu allocation.

### Control Flow, State, And Persistence
Each device owns a LIFO `devres_head` protected by `devres_lock`. Allocation creates a node plus aligned data area and release callback; add/find/remove operate under the lock, usually scanning newest first. Release moves selected nodes to a local todo list under lock, then invokes release callbacks without holding the spinlock. Groups are represented by open/close marker nodes; `remove_nodes()` colors nested groups to release complete group scopes correctly. Managed memory release callbacks often no-op because freeing the devres object frees the payload.

### Dependencies, Integration Points, Risks, And Test Signals
`dd.c` calls `devres_release_all()` during unbind. The file integrates tracing, debug devres logging, slab sizing, rodata detection for const duplication, percpu allocation, page allocator, and Rust post-unbind action removal. Risks include list corruption, overflow in combined allocation size, misuse of managed pointers with the wrong device, group nesting edge cases, and `devm_krealloc()` preserving order while replacing nodes. Test signals include detach unwinding order, group rollback, action remove/release, zero-size allocation, const string handling, krealloc growth/failure, and lockdep with concurrent resource lookup/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/devres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/devtmpfs.c -->
## sources/distributed-fs/ceph-client/drivers/base/devtmpfs.c

### Purpose
`devtmpfs.c` implements the kernel-maintained `/dev` filesystem. It creates an internal tmpfs or ramfs mount, registers a public `devtmpfs` filesystem type that references the existing mount, and serializes device-node create/delete requests through the `kdevtmpfs` kernel thread.

### Important APIs, Types, And Functions
Public entry points are `devtmpfs_init()`, `devtmpfs_mount()`, `devtmpfs_create_node()`, and `devtmpfs_delete_node()`. Internal helpers include `devtmpfs_submit_req()`, `handle_create()`, `handle_remove()`, `create_path()`, `delete_path()`, `dev_mkdir()`, `dev_rmdir()`, `dev_mynode()`, `devtmpfs_work_loop()`, and `devtmpfs_configure_context()`. State includes global `mnt`, worker `thread`, request list, spinlock, and mount boot parameter.

### Control Flow, State, And Persistence
Initialization mounts the backing filesystem with `mode=0755`, configures fs_context ops so external mounts reuse the same superblock, registers the filesystem, and starts `kdevtmpfs` in a private namespace rooted on the internal mount. Device registration calls submit stack-allocated requests, waits for completion, and frees temporary devnode names. Creates derive name, mode, uid/gid, and block/char type from the device, create parent directories, mknod, apply attributes, and tag kernel-created inodes. Deletes verify the inode was created by this thread and matches dev_t/type before unlinking and pruning directories.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include VFS create/remove helpers, init namespace syscalls, tmpfs/ramfs, block-device detection, device devnode callbacks, idmapped mount API, and early boot init ordering. Risks include synchronous request lifetime, worker availability before requests, protecting user-created nodes from deletion, hardlink permission reset, path length/depth handling, and mount option differences under `CONFIG_DEVTMPFS_SAFE`. Test signals include boot auto-mount, nested device node creation/removal, custom devnode ownership/mode, user-created node preservation, block versus char nodes, and fallback to ramfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/devtmpfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/driver.c -->
## sources/distributed-fs/ceph-client/drivers/base/driver.c

### Purpose
`driver.c` provides centralized driver object management: registration/unregistration with a bus, sysfs driver attributes, driver override string handling, and iteration/search over devices currently bound to a driver.

### Important APIs, Types, And Functions
Key APIs are `driver_set_override()`, `driver_for_each_device()`, `driver_find_device()`, `driver_create_file()`, `driver_remove_file()`, `driver_add_groups()`, `driver_remove_groups()`, `driver_register()`, and `driver_unregister()`. `next_device()` adapts a driver klist iterator to `struct device` using `device_private`.

### Control Flow, State, And Persistence
Override setting validates pointers and page-sized sysfs limits, trims embedded NUL behavior through `strlen()`, handles newline-as-clear semantics, swaps the allocated string under the device lock, and frees the old string afterward. Driver iteration initializes a klist iterator at an optional starting device and calls callbacks or match predicates until complete. Registration verifies the bus exists, warns about legacy bus/driver duplicate probe/remove/shutdown callbacks, rejects duplicate names with `driver_find()`, calls `bus_add_driver()`, adds driver attribute groups, emits `KOBJ_ADD`, and extends deferred-probe timeout. Unregister removes groups then removes the driver from the bus.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on bus internals in `base.h`, sysfs, kobject uevents, driver private kobjects, klist lifetime management, and deferred probe extension in `dd.c`. Risks include override lifetime under concurrent sysfs reads, duplicate driver names, partial registration unwind, and iterator callback reference expectations. Test signals include override clear/set with empty and newline input, duplicate registration, group creation failure rollback, driver sysfs file creation, and iterating/removing bound devices under concurrent unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/faux.c -->
## sources/distributed-fs/ceph-client/drivers/base/faux.c

### Purpose
`faux.c` implements a minimal fake bus for devices that need sysfs lifecycle callbacks but no real hardware resources or bus-specific matching. It provides create/destroy helpers and a single always-matching synchronous driver.

### Important APIs, Types, And Functions
`struct faux_object` embeds `struct faux_device` and stores caller ops and sysfs groups. Public APIs are `faux_device_create_with_groups()`, `faux_device_create()`, `faux_device_destroy()`, and init-only `faux_bus_init()`. Internal bus callbacks are `faux_match()`, `faux_probe()`, `faux_remove()`, and `faux_device_release()`.

### Control Flow, State, And Persistence
Initialization allocates and registers a root `faux` device, registers the `faux` bus, then registers `faux_driver`. Creating a device allocates a wrapper, records ops/groups, initializes the embedded device, assigns parent or root, bus, name, release callback, and no-PM flag, then calls `device_add()`. The bus match always succeeds, probe invokes caller `probe`, then adds groups only after successful initialization; group-add failure calls caller remove. Creation tears down the device if binding did not occur. Destroy calls `device_del()` and drops the final reference.

### Dependencies, Integration Points, Risks, And Test Signals
The faux bus depends on the driver core, sysfs groups, `linux/device/faux.h`, and init ordering from `driver_init()`. Risks include unique name requirements, callbacks running before create returns, group creation rollback, root-device lifetime on init failure, and synchronous binding assumptions. Test signals include successful create/destroy, probe failure returning NULL, sysfs group visibility after probe, remove callback ordering, parented and root devices, and init failure unwind for bus/driver registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/faux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware.c -->
## sources/distributed-fs/ceph-client/drivers/base/firmware.c

### Purpose
`firmware.c` creates the global `/sys/firmware` kobject used as the top-level anchor for firmware-related kernel interfaces.

### Important APIs, Types, And Functions
It defines and exports `struct kobject *firmware_kobj`. The only function is init-only `firmware_init()`, which calls `kobject_create_and_add("firmware", NULL)`.

### Control Flow, State, And Persistence
During `driver_init()`, `firmware_init()` creates the top-level kobject. The pointer remains globally available to other subsystems and modules that need to place firmware-oriented sysfs nodes under `/sys/firmware`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies are limited to kobjects, module export support, init annotations, and `base.h`. It integrates with early driver-core initialization before platform, CPU, memory, and other bus setup. Risks are simple but fundamental: allocation failure returns `-ENOMEM`, and users must not assume the pointer exists before driver core init. Test signals are boot-time presence of `/sys/firmware`, successful export consumers, and failure-path propagation if kobject allocation is forced to fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/Kconfig

### Purpose
`Kconfig` defines the firmware loader feature matrix: core firmware loading, debug hashing, Rust abstractions, built-in firmware, sysfs fallback, compressed firmware, suspend caching, and sysfs-based firmware upload.

### Important APIs, Types, And Functions
Important symbols are `FW_LOADER`, `FW_LOADER_DEBUG`, `RUST_FW_LOADER_ABSTRACTIONS`, `FW_LOADER_PAGED_BUF`, `FW_LOADER_SYSFS`, `EXTRA_FIRMWARE`, `EXTRA_FIRMWARE_DIR`, `FW_LOADER_USER_HELPER`, `FW_LOADER_USER_HELPER_FALLBACK`, `FW_LOADER_COMPRESS`, `FW_LOADER_COMPRESS_XZ`, `FW_LOADER_COMPRESS_ZSTD`, `FW_CACHE`, and `FW_UPLOAD`.

### Control Flow, State, And Persistence
The config defaults `FW_LOADER` to enabled and pulls crypto SHA-256 only for debug checksums. Built-in firmware depends on a configured name list and directory. User-helper fallback selects sysfs and paged buffers; forced fallback is a compatibility option also mirrored by sysctl. Compression enables optional XZ and ZSTD paths. Firmware upload selects sysfs and paged buffers because userspace writes data into a loader device before driver-specific flashing.

### Dependencies, Integration Points, Risks, And Test Signals
This file controls which C files build and which paths are compiled inside firmware loader headers. Risks include enabling legacy sysfs fallback without userspace support, GPL/distribution concerns for non-GPL `EXTRA_FIRMWARE`, unsupported compression for built-in firmware, and suspend-cache uevents on platforms where they block sleep. Test signals are build matrix coverage for built-in, modular, fallback, compression, cache, upload, Rust abstraction selection, and sysctl availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/Makefile -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/Makefile

### Purpose
This Makefile wires firmware loader objects into the kernel build according to Kconfig selections.

### Important APIs, Types, And Functions
It builds `firmware_class.o` from `main.o`, conditionally adds `fallback.o`, `fallback_platform.o`, `sysfs.o`, and `sysfs_upload.o`, builds `fallback_table.o` when the user-helper is enabled, and always descends into `builtin/`.

### Control Flow, State, And Persistence
`obj-$(CONFIG_FW_LOADER)` controls the main firmware class object. Conditional `firmware_class-$(CONFIG_...)` lines compose optional features into that object, while `fallback_table.o` is a separate object for exported fallback configuration/sysctl state. `obj-y += builtin/` ensures built-in firmware metadata support participates even when the extra firmware list is empty.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile must stay aligned with `Kconfig` and header `#ifdef`s. Risks include unresolved symbols when sysfs/upload/fallback files are omitted incorrectly, and missing built-in firmware support if the subdirectory is not visited. Test signals include `CONFIG_FW_LOADER=m/y`, combinations of user-helper, EFI embedded firmware, sysfs, upload, and successful link of namespace exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/builtin/Makefile -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/builtin/Makefile

### Purpose
The builtin firmware Makefile generates assembly objects that embed `CONFIG_EXTRA_FIRMWARE` binary blobs and register them in the `.builtin_fw` section.

### Important APIs, Types, And Functions
Key variables are `fwdir`, `firmware`, `FWNAME`, `FWSTR`, `ASM_WORD`, `ASM_ALIGN`, and `PROGBITS`. The `filechk_fwbin` rule emits assembly with firmware data, name string, and a three-word metadata tuple.

### Control Flow, State, And Persistence
`fwdir` resolves absolute or source-tree-relative `CONFIG_EXTRA_FIRMWARE_DIR`. Each configured firmware name becomes a `.gen.S` and `.gen.o`; generated assembly includes the binary with `.incbin`, emits a stable name string, and appends name/data/size records to `.builtin_fw`. The object dependency points directly at the firmware file so missing or changed firmware triggers a rebuild.

### Dependencies, Integration Points, Risks, And Test Signals
This integrates with linker-provided `__start_builtin_fw` and `__end_builtin_fw` consumed by builtin `main.c`. Risks include name mangling collisions, firmware filenames containing commas or separators, architecture-specific `.section` syntax, and lack of compressed extra-firmware support. Test signals include embedding one or more blobs, absolute and relative directories, 32/64-bit builds, ARM section syntax, rebuilds after blob changes, and lookup by original firmware name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/builtin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/builtin/main.c -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/builtin/main.c

### Purpose
`builtin/main.c` implements lookup for firmware blobs linked into the kernel image through `CONFIG_EXTRA_FIRMWARE`.

### Important APIs, Types, And Functions
`struct builtin_fw` mirrors linker metadata. Linker symbols `__start_builtin_fw` and `__end_builtin_fw` delimit the table. Public/internal functions are `firmware_request_builtin()`, `firmware_request_builtin_buf()`, and `firmware_is_builtin()`, with helper `fw_copy_to_prealloc_buf()`.

### Control Flow, State, And Persistence
`firmware_request_builtin()` scans the linker table by name and, on match, points the caller's `struct firmware` directly at read-only built-in data with its size. `firmware_request_builtin_buf()` first performs that lookup and then optionally copies into a caller-provided preallocated buffer if it fits. `firmware_is_builtin()` identifies release paths that must not free built-in data.

### Dependencies, Integration Points, Risks, And Test Signals
The file is active only when `CONFIG_FW_LOADER` is built in. It integrates with `_request_firmware_prepare()` before filesystem lookup and with `release_firmware()`. Risks include table/name mismatch from generated assembly, buffer-too-small failure after a successful lookup, and callers incorrectly releasing stack-owned firmware from early boot APIs. Test signals include built-in hit/miss, preallocated buffer fit/fail, release of built-in firmware, early boot microcode-style lookup, and no allocator involvement for plain builtin requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/builtin/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback.c -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback.c

### Purpose
`fallback.c` implements the legacy sysfs firmware fallback path used when direct filesystem/platform lookup fails or when fallback is forced.

### Important APIs, Types, And Functions
Key APIs are `firmware_fallback_sysfs()`, `kill_pending_fw_fallback_reqs()`, `fw_fallback_set_cache_timeout()`, and `fw_fallback_set_default_timeout()`. Internals include `pending_fw_head`, `fw_load_sysfs_fallback()`, `fw_load_from_user_helper()`, `fw_force_sysfs_fallback()`, and `fw_run_sysfs_fallback()`.

### Control Flow, State, And Persistence
Fallback creates a `fw_sysfs` device, enables paged-buffer loading when no destination buffer exists, adds the firmware request to the pending list under `fw_lock`, optionally sends a uevent with firmware name/timeout/async state, then waits for userspace to complete or abort via sysfs `loading`. Non-uevent/custom fallback waits indefinitely. On timeout or signal, the path aborts the request and deletes the sysfs device. Cache mode temporarily shortens the timeout. Shutdown/suspend can abort pending non-uevent or all requests.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include sysfs loader devices, usermodehelper read locks, LSM `security_kernel_load_data()`, firmware fallback sysctl state, and `fw_priv` completion. Risks include indefinite lingering for custom fallback, interaction with `ignore_sysfs_fallback` and forced fallback, abort races, module shutdown deadlocks, and security policy denial. Test signals include forced fallback, ignored fallback, no-fallback request flags, uevent contents, timeout, custom no-uevent path, suspend/shutdown abort, and userspace writes completing paged-buffer loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback.h -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback.h

### Purpose
`fallback.h` declares firmware fallback entry points and provides no-op stubs when sysfs fallback or platform fallback support is disabled.

### Important APIs, Types, And Functions
It declares `firmware_fallback_sysfs()`, `kill_pending_fw_fallback_reqs()`, `fw_fallback_set_cache_timeout()`, `fw_fallback_set_default_timeout()`, and `firmware_fallback_platform()`, plus inline stubs returning the original error or `-ENOENT`.

### Control Flow, State, And Persistence
The header preserves call-site simplicity: main firmware loading code can call fallback functions unconditionally and receive either real behavior or a compile-time stub. Platform fallback is similarly gated by `CONFIG_EFI_EMBEDDED_FIRMWARE`.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `firmware.h` and `sysfs.h`, so it connects the core state machine with fallback-specific devices. Risks are mostly build-configuration mismatches: stubs must preserve original errors and not accidentally enable fallback semantics. Test signals are compile coverage with user-helper off, EFI embedded firmware off, both enabled, and direct lookup failures preserving errno when fallback is not built.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback_platform.c -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback_platform.c

### Purpose
`fallback_platform.c` loads firmware embedded in platform firmware, such as EFI embedded firmware, when the request opts into platform fallback.

### Important APIs, Types, And Functions
The single function is `firmware_fallback_platform(struct fw_priv *fw_priv)`. It uses `FW_OPT_FALLBACK_PLATFORM`, `efi_get_embedded_fw()`, `security_kernel_load_data()`, `security_kernel_post_load_data()`, `vmalloc()`, and `fw_state_done()`.

### Control Flow, State, And Persistence
The function first verifies the request option, asks LSMs whether firmware loading is allowed, looks up embedded data by firmware name, checks that it fits a preallocated buffer if present, runs post-load security validation, allocates a buffer when needed, copies the platform data, stores size, and marks the firmware request complete.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates with the main request flow after filesystem and compressed lookup fail but before sysfs fallback. Dependencies include EFI embedded firmware support, security hooks, and vmalloc. Risks include copying untrusted platform data without security approval, buffer-too-small handling, distinguishing `-ENOENT` from policy errors, and memory ownership by `fw_priv`. Test signals include opt-in versus no-opt behavior, embedded hit/miss, LSM denial, preallocated buffer size checks, and release freeing allocated copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback_table.c -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback_table.c

### Purpose
`fallback_table.c` owns runtime configuration for firmware sysfs fallback and exposes sysctls under `kernel/firmware_config`.

### Important APIs, Types, And Functions
It defines exported namespace symbol `fw_fallback_config` with `force_sysfs_fallback`, `ignore_sysfs_fallback`, `loading_timeout`, and `old_timeout`. With sysctl enabled it provides `register_firmware_config_sysctl()` and `unregister_firmware_config_sysctl()`.

### Control Flow, State, And Persistence
The initial force value follows `CONFIG_FW_LOADER_USER_HELPER_FALLBACK`, and default timeout is 60 seconds. Registering creates a sysctl table for `force_sysfs_fallback` and `ignore_sysfs_fallback`, both clamped between 0 and 1. Unregistering removes the table and clears the header pointer.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include sysctl, exported symbol namespaces, and fallback/sysfs headers. It is consumed by `fallback.c` and `sysfs.c` timeout handlers. Risks include global mutable policy affecting all firmware requests, sysctl unavailable builds relying on defaults, and force/ignore precedence. Test signals include sysctl registration, min/max enforcement, forced fallback with helper enabled, ignored fallback suppressing sysfs devices, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/firmware.h -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/firmware.h

### Purpose
`firmware.h` defines the shared internal firmware-loader state machine, request option flags, private firmware buffer object, and cross-file interfaces.

### Important APIs, Types, And Functions
Important enums are `fw_opt` and `fw_status`. Core structures are `struct fw_state` and `struct fw_priv`, with optional paged-buffer and user-helper fields. It declares `fw_lock`, `fw_cache`, `fw_load_abort_all`, `alloc_lookup_fw_priv()`, `assign_fw()`, `free_fw_priv()`, `fw_state_init()`, built-in firmware helpers, and paged-buffer helpers. Inline state functions cover wait, set, start, done, aborted, and status checks.

### Control Flow, State, And Persistence
`fw_priv` is the refcounted shared object for one firmware load, including data pointer, size, allocated size, offset, options, firmware name, cache owner, completion, and optional pages. State transitions move from unknown to loading to done or aborted; done/abort completes all waiters and removes pending fallback entries. `__fw_state_wait_common()` maps abort to `-ENOENT`, timeout to `-ETIMEDOUT`, and signal interruption through the wait helper.

### Dependencies, Integration Points, Risks, And Test Signals
The header ties together main lookup, builtin lookup, fallback, sysfs, upload, cache, and compression paths. Risks include global lock coupling, completion status races, list deletion only when fallback fields exist, and option flag interactions such as partial reads requiring preallocated buffers. Test signals include batched request completion, abort wakeups, timeout behavior, paged-buffer builds off/on, user-helper builds off/on, and builtin helper stubs for modular cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/main.c -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/main.c

### Purpose
`main.c` implements the firmware loader public API: synchronous, direct, platform, into-buffer, partial, asynchronous, cache, compressed, and release paths. It coordinates built-in firmware, filesystem lookup, decompression, platform fallback, sysfs fallback, request batching, suspend caching, and shutdown cleanup.

### Important APIs, Types, And Functions
Public APIs include `request_firmware()`, `firmware_request_nowarn()`, `request_firmware_direct()`, `firmware_request_platform()`, `firmware_request_cache()`, `request_firmware_into_buf()`, `request_partial_firmware_into_buf()`, `release_firmware()`, `request_firmware_nowait()`, and `firmware_request_nowait_nowarn()`. Important internals are `struct firmware_cache`, `struct fw_cache_entry`, `alloc_lookup_fw_priv()`, `fw_get_filesystem_firmware()`, decompression helpers, `_request_firmware_prepare()`, `_request_firmware()`, `assign_fw()`, paged-buffer helpers, cache PM callbacks, and module init/exit.

### Control Flow, State, And Persistence
Requests validate firmware name and reject `..` path components, try built-in firmware, batch with an existing `fw_priv` unless no-cache/partial, then read from configured firmware paths in the init mount namespace under kernel credentials. Full reads may try `.zst`, `.xz`, platform fallback, and sysfs fallback after raw lookup failure; partial reads stay direct. Success marks state done and assigns data at the last moment. Batched requesters wait on the same completion. Release either frees direct vmalloc data or drops the shared `fw_priv` ref. PM cache records firmware names in devres, caches before suspend, and uncaches after resume.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include initramfs, kernel file reading, LSM firmware hooks, vmalloc/vmap, XZ/ZSTD, async work, PM/reboot notifiers, syscore suspend, devres, fallback/sysfs, and builtin firmware linker tables. Risks include request batching with failed loads, no-cache buffer ownership, decompression size validation, path handling, suspend-cache deadlocks, fallback abort semantics, and firmware data lifetime across async callbacks. Test signals include all public APIs, batched concurrent same-name requests, invalid path rejection, search path priority, compressed fallback, platform fallback, sysfs fallback, partial offset reads, suspend/resume cache, shutdown abort, and release of built-in vs allocated firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs.c -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs.c

### Purpose
`sysfs.c` implements the firmware class and per-request sysfs device used by fallback downloads and firmware upload registration.

### Important APIs, Types, And Functions
Important APIs are `register_sysfs_loader()`, `unregister_sysfs_loader()`, `__fw_load_abort()`, `fw_create_instance()`, and device attributes `loading` plus binary `data`. With user-helper enabled it exposes class timeout and uevent generation. Internal helpers include `firmware_loading_store()`, `firmware_data_read()`, `firmware_data_write()`, `fw_realloc_pages()`, and paged/direct read-write helpers.

### Control Flow, State, And Persistence
Class registration creates `/sys/class/firmware` and optional fallback sysctls. `fw_create_instance()` initializes a firmware class device named after the firmware and parented to the requester. Userspace writes `1` to `loading` to start/reset, writes firmware bytes to `data`, then writes `0` to map pages, run post-load security checks, mark done, and potentially start a firmware upload worker. Writing `-1` aborts and resets upload state when needed. Data writes require `CAP_SYS_RAWIO`, grow paged buffers, or copy into preallocated memory.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include sysfs class devices, binary attributes, firmware state, LSM post-load checks, highmem page copy helpers, fallback config, and upload hooks. Risks include holding `fw_lock` around user-visible state, racing writes after done/abort, page growth failure aborting loads, static variable misuse in visibility, and correct reset for upload reuse. Test signals include timeout show/store, uevent variables, loading 1/0/-1 state transitions, permission checks, paged buffer growth/map, preallocated buffer bounds, security rejection, and upload attribute visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs.h -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs.h

### Purpose
`sysfs.h` declares firmware class sysfs interfaces, fallback configuration accessors, `struct fw_sysfs`, and upload integration hooks.

### Important APIs, Types, And Functions
It imports the `FIRMWARE_LOADER_PRIVATE` namespace, declares `fw_fallback_config`, `dev_attr_loading`, registration helpers, `struct fw_sysfs`, `to_fw_sysfs()`, `__fw_load_abort()`, `fw_load_abort()`, `fw_create_instance()`, and upload attribute/hooks when `CONFIG_FW_UPLOAD` is enabled.

### Control Flow, State, And Persistence
When user-helper is enabled, inline accessors read and write the global fallback timeout. When sysfs support is disabled, registration functions stub out to success. `fw_sysfs` stores the class device, firmware object, private firmware state, async flag, and optional upload private data.

### Dependencies, Integration Points, Risks, And Test Signals
The header connects fallback, sysfs, upload, and core firmware state. Risks are configuration-dependent stubs hiding missing sysfs behavior, namespace import requirements, and callers assuming upload hooks exist when compiled out. Test signals include build coverage for sysfs off, user-helper off, upload off, timeout helper use, and aborting through a `fw_sysfs` wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs_upload.c -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs_upload.c

### Purpose
`sysfs_upload.c` implements user-initiated firmware update devices under the firmware sysfs class. Drivers register upload operations, userspace writes an image via the common `loading`/`data` interface, and a worker transfers it to device-specific flash/update logic.

### Important APIs, Types, And Functions
Public APIs are `firmware_upload_register()` and `firmware_upload_unregister()`. Sysfs attributes are `status`, `error`, `cancel`, and `remaining_size`. Important internals are `fw_upload_start()`, `fw_upload_free()`, `fw_upload_main()`, `fw_upload_is_visible()`, progress/error string helpers, and progress/error setters.

### Control Flow, State, And Persistence
Registration validates name and required ops, pins the module, allocates public/private upload objects, creates a firmware class instance, allocates a no-cache paged `fw_priv`, marks it paged, and adds the device. After userspace completes a sysfs load, `fw_upload_start()` checks for nonzero data and idle state, references the parent, records data and size, resets errors, and queues `fw_upload_main()` on `system_long_wq`. The worker calls driver `prepare`, repeated `write`, `poll_complete`, optional `cleanup`, frees paged buffers, resets firmware state, drops the parent, and returns to idle. Unregister cancels active uploads and flushes work before device unregister.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include firmware sysfs, `fw_priv` paged buffers, module refs, workqueues, upload ops, and parent device references. Risks include zero-byte writes, driver write returning zero, cancellation races, preserving remaining size on errors, not exposing upload attributes for non-upload fallback devices, and ensuring module/device lifetime through worker completion. Test signals include registration validation, upload success, each error code/progress string, cancel while active, unregister while active, zero-size upload reset, repeated uploads, and failed driver write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs_upload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs_upload.h -->
## sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs_upload.h

### Purpose
`sysfs_upload.h` defines private state for sysfs firmware upload workers and progress tracking.

### Important APIs, Types, And Functions
It defines `enum fw_upload_prog` values `IDLE`, `RECEIVING`, `PREPARING`, `TRANSFERRING`, `PROGRAMMING`, and `MAX`. `struct fw_upload_priv` stores the public `fw_upload`, owner module, name, ops, mutex, worker, data pointer, remaining size, current progress, error progress, and error code.

### Control Flow, State, And Persistence
The upload implementation transitions progress from idle to receiving when sysfs data is accepted, then through preparing, transferring, and programming in the worker. Error state records the phase where an operation failed and remains readable once progress returns to idle. Remaining size is intentionally preserved on failures until the next upload begins.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on `sysfs.h` and public firmware upload ops/types. Risks include progress enum/string table drift, insufficient locking around fields, and stale data pointer lifetime if the worker/reset path changes. Test signals include enum coverage in string arrays, error reporting format, remaining-size semantics, and concurrent status/error/cancel reads while the worker updates progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs_upload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/hypervisor.c -->
## sources/distributed-fs/ceph-client/drivers/base/hypervisor.c

### Purpose
`hypervisor.c` creates the global `/sys/hypervisor` kobject used as the top-level anchor for hypervisor-specific sysfs interfaces.

### Important APIs, Types, And Functions
It defines and exports `struct kobject *hypervisor_kobj`. `hypervisor_init()` creates the kobject with `kobject_create_and_add("hypervisor", NULL)`.

### Control Flow, State, And Persistence
During driver core initialization, `hypervisor_init()` creates the root kobject. The pointer persists globally for architecture or hypervisor code that needs to add child kobjects or attributes below `/sys/hypervisor`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies are kobjects, device headers, exports, and init ordering from `driver_init()`. Risks are allocation failure and consumers using the pointer before initialization. Test signals include boot presence of `/sys/hypervisor`, exported symbol use by hypervisor-specific code, and clean error return under allocation-failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/hypervisor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/init.c -->
## sources/distributed-fs/ceph-client/drivers/base/init.c

### Purpose
`init.c` orders early initialization of the Linux driver model and core pseudo-buses/devices.

### Important APIs, Types, And Functions
The only function is `driver_init()`. It calls initialization for noop backing device info, devtmpfs, devices, buses, classes, firmware, hypervisor, faux bus, Open Firmware core, software nodes, platform bus, auxiliary bus, memory, node, CPU, and container devices.

### Control Flow, State, And Persistence
`driver_init()` is called early from kernel init. It first initializes foundational pieces required by later device registration: backing info, devtmpfs, generic device/bus/class infrastructure, and top-level firmware/hypervisor kobjects. It then initializes higher-level core buses and device classes that depend on the core being present.

### Dependencies, Integration Points, Risks, And Test Signals
The file is an integration point rather than a feature body. Risks are ordering regressions: later init calls assume sysfs, buses, classes, devtmpfs, and top-level kobjects already exist. Test signals include boot smoke tests, initcall ordering checks, `/dev` population, platform/auxiliary bus availability, CPU and node sysfs presence, and failure injection in individual init routines where callers expect panic or propagated errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/isa.c -->
## sources/distributed-fs/ceph-client/drivers/base/isa.c

### Purpose
`isa.c` implements a simple ISA bus wrapper for legacy ISA drivers that create a fixed number of logical devices and bind them to a driver-specific callback table.

### Important APIs, Types, And Functions
It defines root `isa_bus`, `struct isa_dev`, `isa_bus_type`, and callbacks for match, probe, remove, shutdown, suspend, and resume. Public APIs are `isa_register_driver()` and `isa_unregister_driver()`. Init function `isa_bus_init()` registers the bus and root device at `postcore_initcall`.

### Control Flow, State, And Persistence
Driver registration assigns the ISA bus to the embedded driver, registers it, then allocates `ndev` `isa_dev` objects named `<driver>.<id>`. Each device stores the `isa_driver` in `platform_data`, has the ISA root as parent, 24-bit DMA mask, and a release callback. Matching succeeds only for devices whose `platform_data` points to the probing `isa_driver`, optionally filtered by `isa_driver->match`; a failed optional match clears `platform_data` so it will not bind. Unregister walks the driver's device list and unregisters each before unregistering the driver.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include driver core bus registration, DMA masks, legacy `struct isa_driver`, and platform_data. Risks include partial registration unwind, linked-list lifetime during unregister, clearing platform_data after failed match, no devices returning `-ENODEV`, and legacy PM callbacks. Test signals include multi-device registration, match rejection, probe/remove/shutdown callbacks with IDs, 24-bit DMA mask setup, registration failure rollback, and postcore root bus presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/isa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/map.c -->
## sources/distributed-fs/ceph-client/drivers/base/map.c

### Purpose
`map.c` implements `kobj_map`, a dev_t-to-kobject lookup table used by character/block device infrastructure to find the kobject that owns a device number.

### Important APIs, Types, And Functions
`struct kobj_map` holds 255 hash buckets of `struct probe` lists and an external mutex. Public APIs are `kobj_map()`, `kobj_unmap()`, `kobj_lookup()`, and `kobj_map_init()`. Each probe records base dev_t, range, module owner, lookup callback, optional lock callback, and data.

### Control Flow, State, And Persistence
Mapping allocates one probe entry per covered major bucket, caps bucket span at 255, initializes identical metadata, and inserts entries sorted by ascending range so narrower mappings win. Unmap removes matching range entries from every bucket and frees the allocated block once. Lookup scans the bucket for mappings covering the dev_t, skips ranges no better than the best failed range, pins the module, optionally calls a lock callback, drops the map mutex, invokes the probe callback, releases the module, and retries if the callback returns NULL.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include dev_t major/minor encoding, module refs, kobjects, mutexes, and callbacks from block/char device registries. Risks include poor scaling for large dev_t spaces, sorted range ordering correctness, retry behavior after callbacks mutate mappings, owner protection covering only the probe call, and freeing shared allocation from any bucket removal. Test signals include overlapping ranges preferring smaller range, lookup retry after failed probe, module ref failure, lock callback denial, unmap across multiple majors, and base probe fallback covering the whole space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/map.c -->
