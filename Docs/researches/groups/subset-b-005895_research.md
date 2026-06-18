# Research: subset-b-005895

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/ubi.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/ubi.h

Purpose: defines the in-kernel public API for UBI volumes on MTD devices, including volume/device metadata, open modes, notification payloads, scatter-gather reads, logical eraseblock operations, and synchronization.

Important APIs and types: `UBI_ALL`, `UBI_MAX_SG_COUNT`, and open modes `UBI_READONLY`, `UBI_READWRITE`, `UBI_EXCLUSIVE`, and `UBI_METAONLY` define caller intent. `struct ubi_volume_info` reports volume identity, size, static-volume corruption/update markers, alignment-derived usable LEB size, name, device node, and character-device identity. `struct ubi_device_info` describes the UBI device geometry and read-only state. `struct ubi_sgl` wraps up to 64 `scatterlist` entries with cursor fields for repeated `ubi_leb_read_sg()` calls, initialized by `ubi_sgl_init()`. `struct ubi_notification` carries device and volume snapshots for notifier callbacks. Exported operations include `ubi_get_device_info()`, `ubi_get_volume_info()`, `ubi_open_volume*()`, notifier registration, `ubi_close_volume()`, LEB read/write/change/erase/unmap/map/is_mapped, `ubi_sync()`, and convenience `ubi_read()`/`ubi_read_sg()` wrappers.

Control flow: callers open a volume by device/volume id, name, or path in a declared mode, perform LEB-level I/O, mapping, erase, or synchronization, then close the opaque `ubi_volume_desc`. Read calls can request static-volume data checking, while wrapper reads deliberately disable that check. Scatter-gather reads advance through `ubi_sgl` cursor state across calls. Volume lifecycle events are delivered through the Linux notifier chain with add/remove/resize/rename/shutdown/update event codes.

State and persistence: the header exposes persistent flash-backed UBI volume state through metadata snapshots, but it owns only transient descriptor and scatter-gather cursor state. The `corrupted` and `upd_marker` fields are durable health indicators for static volume data and interrupted updates; LEB map/unmap/erase/write operations mutate flash allocation and contents through the UBI core.

Dependencies and integration points: depends on ioctl/type definitions, scatterlists, `mtd/ubi-user.h`, notifier blocks, devices, and char-device numbers. Integrates MTD-backed UBI with kernel clients such as filesystems, volume managers, and code that reacts to volume lifecycle notifications.

Risks and test signals: risks include using write APIs on read-only or metadata-only descriptors, mishandling static-volume corruption versus update markers, offset/length alignment against `usable_leb_size`, stale notifier assumptions during detach, and incorrect scatterlist initialization before `ubi_leb_read_sg()`. Test signals include UBI attach/detach, named and path opens, static-volume checked reads, interrupted volume updates, notifier replay with `ignore_existing` variants, LEB map/unmap/is_mapped behavior, scatter-gather reads crossing entries, and `ubi_sync()` after writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/ubi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/xip.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/xip.h

Purpose: provides MTD execute-in-place support primitives for code paths that must keep servicing interrupts and timing delays while flash is temporarily not in array/read mode during writes or erases.

Important APIs and types: when `CONFIG_MTD_XIP` is enabled it includes architecture primitives from `asm/mtd-xip.h`. `__xipram` marks flash-state-changing functions for RAM placement under `CONFIG_XIP_KERNEL`; otherwise it compiles away. Required architecture macros are `xip_irqpending()`, `xip_currtime()`, `xip_elapsed_since(x)`, and `xip_iprefetch()`, with optional `xip_cpu_idle()`. Missing primitives degrade to zero/no-op definitions with compile-time warnings.

Control flow: flash algorithms that cannot execute from flash use `__xipram` and periodically call the architecture-provided IRQ/time/prefetch/idle hooks while waiting for hardware operations. If an architecture does not define the hooks, support compiles but responsiveness during flash write/erase is intentionally limited.

State and persistence: no persistent state is owned by this header. Runtime behavior is direct hardware polling and timing through architecture hooks while the underlying MTD device is outside normal read-array mode.

Dependencies and integration points: depends on compiler attributes and architecture-specific MTD XIP support. It connects generic MTD flash code, XIP-kernel placement, interrupt responsiveness, and platform timer/idle primitives.

Risks and test signals: risks include executing unavailable flash-resident code while flash is not readable, inaccurate elapsed-time conversions, overflow in platform timers, lost interrupt responsiveness when primitives are missing, and misplacing `__xipram` functions. Test with XIP kernel builds, flash erase/write under interrupt load, platforms with and without `xip_iprefetch()`/`xip_cpu_idle()`, and compile warnings for missing architecture hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/xip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtio.h -->
# sources/distributed-fs/ceph-client/include/linux/mtio.h

Purpose: supplies compat ioctl helpers for magnetic tape drivers that need to return `MTIOCGET` and `MTIOCPOS` data correctly to 32-bit userspace running on a 64-bit kernel.

Important APIs and types: `struct mtget32` and `struct mtpos32` define the 32-bit layouts for incompatible tape status/position structures, with ioctl numbers `MTIOCGET32` and `MTIOCPOS32`. `put_user_mtget()` converts a native `struct mtget` into the compat layout when `in_compat_syscall()` is true and copies the native structure otherwise. `put_user_mtpos()` writes the block number as either `u32` or `long` depending on syscall mode.

Control flow: tape ioctl implementations populate native kernel `struct mtget` or `struct mtpos` data, then call these helpers to copy results to the user pointer in the ABI shape selected by the current syscall context. Copy failures are converted to `-EFAULT`.

State and persistence: no state is kept. The helpers only marshal transient ioctl response data from kernel memory to userspace.

Dependencies and integration points: depends on compat detection, UAPI tape structures, and user access helpers. It integrates SCSI/IDE tape-style drivers with the generic compat ioctl layer.

Risks and test signals: risks include truncating fields that exceed signed 32-bit ranges, returning native layout to compat callers, incorrect user pointer type in `put_user_mtpos()`, and missing `-EFAULT` propagation. Test native and compat `MTIOCGET`/`MTIOCPOS`, invalid user pointers, large block/file numbers, and all tape drivers that share the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mutex.h -->
# sources/distributed-fs/ceph-client/include/linux/mutex.h

Purpose: declares the main kernel mutex API, initializers, lockdep/debug integration, PREEMPT_RT variants, device-managed initialization, lock operations, and cleanup-based guard helpers.

Important APIs and types: `mutex_init()`, `mutex_init_with_key()`, `__MUTEX_INITIALIZER()`, and `DEFINE_MUTEX()` initialize mutexes with debug and lockdep metadata. Non-RT builds initialize `owner`, `wait_lock`, `first_waiter`, and optional debug fields; PREEMPT_RT builds wrap `rt_mutex_base`. Locking APIs include `mutex_lock()`, `mutex_lock_interruptible()`, `mutex_lock_killable()`, `mutex_lock_io()`, nested/nest-lock variants under lockdep, `mutex_trylock()`, `mutex_unlock()`, `mutex_is_locked()`, `mutex_get_owner()`, and `atomic_dec_and_mutex_lock()`. `devm_mutex_init()` registers debug teardown when `CONFIG_DEBUG_MUTEXES` needs it. `DEFINE_LOCK_GUARD_1*` and class constructor macros provide scoped cleanup lock guards for mutex, try, interruptible, killable, and init use.

Control flow: static locks are created with `DEFINE_MUTEX`, dynamic locks call `mutex_init()`, and callers acquire/release through blocking, interruptible, killable, trylock, or I/O-accounted paths. With `CONFIG_DEBUG_LOCK_ALLOC`, public APIs route through nested forms so lockdep receives subclass or nesting relationships. With PREEMPT_RT, the same API maps to rtmutex internals to provide priority inheritance semantics.

State and persistence: mutex state is in-memory synchronization state: owner, waiters, lockdep map, optional magic/debug fields, or rtmutex state. It is not persistent and must not be copied, memset-reinitialized while held, freed while held, or used from interrupt context.

Dependencies and integration points: depends on current task, atomic operations, spinlock and osq types, lockdep, debug locks, cleanup guard macros, RT mutexes when enabled, and device-managed resource cleanup. It is a core synchronization contract used across the kernel.

Risks and test signals: risks include recursive locking, non-owner unlock, reinitializing or freeing held locks, ignoring return values from interruptible/killable APIs, lockdep subclass mistakes, PREEMPT_RT semantic drift, and misuse of scoped guards that changes unlock timing. Test signals include `CONFIG_DEBUG_MUTEXES`, `CONFIG_DEBUG_LOCK_ALLOC`, lockdep cycle detection, PREEMPT_RT builds, interruptible signal handling, trylock contention, devm teardown, and cleanup guard scope-exit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mutex_api.h -->
# sources/distributed-fs/ceph-client/include/linux/mutex_api.h

Purpose: compatibility wrapper that exposes the mutex API by including `linux/mutex.h`.

Important APIs and types: it defines no independent symbols; all API surface comes from `mutex.h`.

Control flow: include users that still reference `linux/mutex_api.h` are routed directly to the canonical mutex declarations.

State and persistence: no state is owned here.

Dependencies and integration points: depends solely on `linux/mutex.h`. It preserves source compatibility for code that includes the older split API header.

Risks and test signals: risk is header dependency drift if `mutex.h` changes include guards or ordering. Test by compiling include users and ensuring no duplicate declarations or missing mutex symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mutex_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mutex_types.h -->
# sources/distributed-fs/ceph-client/include/linux/mutex_types.h

Purpose: defines the storage layout and semantic contract for `struct mutex`, separated from the higher-level API declarations in `mutex.h`.

Important APIs and types: non-RT `context_lock_struct(mutex)` contains `atomic_long_t owner`, `raw_spinlock_t wait_lock`, optional optimistic spin queue `osq`, guarded `first_waiter`, optional debug `magic`, and optional `lockdep_map`. PREEMPT_RT uses `struct rt_mutex_base rtmutex` plus optional lockdep metadata. The comments document strict mutex rules: one owner, owner-only unlock, no recursive locking, no copying or memset initialization, no held-lock exit/free/reinit, and no interrupt-context use.

Control flow: higher-level mutex APIs allocate, initialize, and mutate this state. Waiters serialize through `wait_lock`, optimistic spinning uses `osq` when configured, and RT builds delegate wait/ownership behavior to rtmutex internals.

State and persistence: all fields are volatile in-memory lock state. Debug and lockdep fields persist only for the lifetime of the mutex object and help detect misuse; there is no durable state.

Dependencies and integration points: depends on atomic, lockdep, osq, spinlock, type definitions, and `rtmutex.h` on PREEMPT_RT. It is included by lock users needing the concrete type but not necessarily the full API.

Risks and test signals: risks include ABI/layout assumptions outside the locking core, failing to respect RT versus non-RT layout, racing direct field access, and missing debug enforcement in non-debug builds. Test with lockdep/debug mutex configs, optimistic spinning configs, PREEMPT_RT, structure initialization paths, and misuse tests for recursive lock/unlock/free cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mutex_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mux/consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/mux/consumer.h

Purpose: declares the consumer-side multiplexer API for drivers that need to acquire a mux control or named mux state, select it, optionally delay after switching, try-select without blocking, and deselect it.

Important APIs and types: opaque `struct mux_control` and `struct mux_state` are manipulated through `mux_control_states()`, `mux_control_select_delay()`, `mux_state_select_delay()`, try-select variants, inline zero-delay wrappers, `mux_control_deselect()`, `mux_state_deselect()`, `mux_control_get()`, optional get, put, and device-managed get helpers including preselected state variants. When `CONFIG_MULTIPLEXER` is disabled, required gets return `ERR_PTR(-EOPNOTSUPP)`, optional gets return `NULL`, and operations return `-EOPNOTSUPP`.

Control flow: a consumer obtains a mux control or state from device resources, selects the desired state before accessing the downstream resource, optionally observes a settle delay, performs its operation, then deselects or lets devm cleanup release resources. Try-select paths let consumers avoid sleeping or avoid contended selection.

State and persistence: consumer-visible state is the selected mux state held in the mux core and hardware. The header itself stores none; devm helpers bind lifetime to the requesting device.

Dependencies and integration points: depends on the multiplexer core and device model. It integrates I2C/SPI/regulator/PHY-style consumers with mux providers through firmware-described or platform-described mux resources.

Risks and test signals: risks include ignoring `ERR_PTR` versus optional `NULL`, forgetting deselect on error paths, assuming disabled-config stubs succeed, using state counts without validating indices, and missing hardware settle delays. Test enabled and disabled `CONFIG_MULTIPLEXER`, optional resource absence, contended try-select, devm cleanup, preselected state helpers, and error unwinding that must deselect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mux/consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mux/driver.h -->
# sources/distributed-fs/ceph-client/include/linux/mux/driver.h

Purpose: declares the provider-side multiplexer core structures and registration APIs used by mux controller drivers.

Important APIs and types: `struct mux_control_ops` exposes the provider `set()` callback. `struct mux_control` holds a semaphore lock, parent chip, cached state, number of states, idle state, and last-change timestamp. `struct mux_chip` embeds a device, controller count, internal id, ops pointer, and a flexible counted array of mux controls. Helpers include `to_mux_chip()`, `mux_chip_priv()`, allocation/register/unregister/free, devm allocation/register, and `mux_control_get_index()`.

Control flow: a driver allocates a mux chip with a controller count and private tailroom, initializes per-controller `states` and `idle_state` plus chip ops, registers the chip, and the mux core calls `ops->set()` under mux locking when consumers select/deselect states. Unregister and free release device-model resources.

State and persistence: mux state is in-memory cached selection plus hardware state programmed by provider callbacks. `last_change` supports delay/settle calculations; idle state determines what the core programs when no consumer is active.

Dependencies and integration points: depends on device model, DT mux bindings for idle-state constants, `ktime`, and semaphores. It integrates platform mux hardware providers with the consumer API.

Risks and test signals: risks include drivers modifying `cached_state`, wrong flexible-array private-memory sizing, incorrect idle-state semantics, missing locking in provider callbacks, and stale cached state after hardware reset. Test multi-controller chips, private data access via `mux_chip_priv()`, register/unregister/devm cleanup, idle disconnect/as-is behavior, delay-sensitive consumers, and hardware reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mux/driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mv643xx_eth.h -->
# sources/distributed-fs/ceph-client/include/linux/mv643xx_eth.h

Purpose: defines platform data, register layout constants, and board configuration fields for the Marvell MV643xx Ethernet driver.

Important APIs and types: constants name the shared and port platform devices, shared register base/size, BAR and address enable registers, checksum default limit, PHY address encodings, and `MV643XX_ETH_PHY_NONE`. `struct mv643xx_eth_shared_platform_data` provides DRAM target info and optional TX checksum packet-size limit. `struct mv643xx_eth_platform_data` links a port to the shared platform device, port number, PHY address or node, override MAC address, fixed or autonegotiated speed/duplex, PHY interface mode, RX/TX queue counts and sizes, and optional SRAM descriptor regions.

Control flow: board or platform setup fills these structures before registering the shared Ethernet device and per-port devices. The driver reads shared data to program memory windows/checksum limits and per-port data to configure PHY, MAC identity, queue topology, descriptor rings, and optional SRAM-backed descriptors.

State and persistence: this header describes boot-time platform configuration. Runtime link state, descriptor state, and hardware registers live in the Ethernet driver and device.

Dependencies and integration points: depends on Marvell MBUS DRAM target info, Ethernet address constants, PHY definitions, `platform_device`, and device-tree nodes. It bridges legacy platform-data board files with the MV643xx netdev driver.

Risks and test signals: risks include invalid PHY address encoding, MAC override misuse, queue count/size mismatch with SRAM capacity, checksum limit assumptions, and stale platform-data use alongside device-tree descriptions. Test platform-data boot, multiple ports sharing registers, fixed and PHY-negotiated links, SRAM descriptor allocation, queue size overrides, and large-packet checksum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mv643xx_eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mv643xx_i2c.h -->
# sources/distributed-fs/ceph-client/include/linux/mv643xx_i2c.h

Purpose: defines the platform data contract for the Marvell MV64xxx I2C controller driver.

Important APIs and types: `MV64XXX_I2C_CTLR_NAME` names the controller driver, and `struct mv64xxx_i2c_pdata` carries clock divider fields `freq_m`, `freq_n`, and transfer timeout in milliseconds.

Control flow: platform code provides divider and timeout values at device creation; the I2C controller driver converts them into bus timing and timeout behavior during probe and transfers.

State and persistence: no runtime state is owned here. The structure is boot-time configuration for hardware registers and transfer policy.

Dependencies and integration points: depends on fixed-width Linux types and integrates board/platform data with the MV64xxx I2C adapter driver.

Risks and test signals: risks include invalid clock divisors, timeout values that are too short or too long, and mismatched platform-data naming. Test probe with platform data, expected bus frequency, transfer timeout paths, and error recovery on stuck buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mv643xx_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mvebu-pmsu.h -->
# sources/distributed-fs/ceph-client/include/linux/mvebu-pmsu.h

Purpose: declares the Marvell EBU PMSU dynamic frequency scaling request hook with a stub for non-MVEBU builds.

Important APIs and types: `mvebu_pmsu_dfs_request(int cpu)` is exported when `CONFIG_MACH_MVEBU_V7` is enabled and otherwise inlines to `-ENODEV`.

Control flow: CPU/clock/power-management code calls this helper to request a DFS transition for a CPU on supported MVEBU V7 platforms. Unsupported builds fail fast without requiring callers to carry their own `#ifdef`.

State and persistence: no state is stored here. Actual CPU power/frequency state is owned by PMSU/platform code and hardware.

Dependencies and integration points: integrates MVEBU platform support with generic callers that may compile on many architectures. The fallback uses the common `-ENODEV` capability-absent convention.

Risks and test signals: risks include callers treating `-ENODEV` as a transient failure, missing errno includes through transitive dependencies, and platform support drift. Test MVEBU and non-MVEBU builds, DFS request success/failure, CPU hotplug interactions, and callers' handling of unsupported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mvebu-pmsu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mxm-wmi.h -->
# sources/distributed-fs/ceph-client/include/linux/mxm-wmi.h

Purpose: declares helper calls for the MXM WMI driver to invoke GPU-adapter-related WMI methods.

Important APIs and types: adapter constants identify discrete and integrated adapters: `MXM_MXDS_ADAPTER_0`, `MXM_MXDS_ADAPTER_1`, and `MXM_MXDS_ADAPTER_IGD`. Functions `mxm_wmi_call_mxds()`, `mxm_wmi_call_mxmx()`, and `mxm_wmi_supported()` expose WMI method invocation and support probing.

Control flow: graphics/platform code checks `mxm_wmi_supported()` and invokes MXDS/MXMX methods for a selected adapter when platform firmware exposes the MXM WMI interface.

State and persistence: no state is stored in the header. Runtime state is firmware/WMI availability and side effects of invoked ACPI methods.

Dependencies and integration points: integrates GPU/ACPI platform handling with the MXM WMI driver. The API is intentionally small and firmware-method oriented.

Risks and test signals: risks include the two discrete adapter constants both being `0x0`, unsupported firmware paths, method side effects that differ by vendor, and missing support checks before calls. Test with systems exposing MXM WMI, unsupported systems, discrete/integrated adapter paths, and error propagation from WMI calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mxm-wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/namei.h -->
# sources/distributed-fs/ceph-client/include/linux/namei.h

Purpose: declares VFS pathname lookup, parent lookup, creation/removal/rename setup, mount following, scoped lookup flags, symlink limits, and helper utilities used by filesystem and kernel path consumers.

Important APIs and types: constants include `MAX_NESTED_LINKS`, `MAXSYMLINKS`, final-component types `LAST_*`, pathwalk flags `LOOKUP_*`, intent flags for open/create/exclusive/rename target, and scoping flags `LOOKUP_NO_SYMLINKS`, `LOOKUP_NO_MAGICLINKS`, `LOOKUP_NO_XDEV`, `LOOKUP_BENEATH`, `LOOKUP_IN_ROOT`, and `LOOKUP_IS_SCOPED`. Lookup APIs include `user_path_at()`, `kern_path()`, `kern_path_parent()`, `vfs_path_lookup()`, `vfs_path_parent_lookup()`, no-permission lookup helpers, and `lookup_one*()` variants. Directory operation helpers include `start_creating_path()`, `start_removing_path()`, `start_creating()`, `start_removing()`, noperm/dentry/killable variants, `end_creating()`, `end_creating_keep()`, and `end_removing()`. Rename helpers are `start_renaming*()` and `end_renaming()`. Other helpers include `follow_down_one()`, `follow_down()`, `follow_up()`, `mode_strip_umask()`, `nd_jump_link()`, `nd_terminate_link()`, and `retry_estale()`.

Control flow: callers use lookup flags to resolve a path from user or kernel memory, optionally request parent/final-component information, then start a create/remove/rename operation that locks and pins relevant dentries before invoking VFS operations. Finish helpers release or retain dentries consistently. Stale network filesystem results can be retried by adding `LOOKUP_REVAL` when `retry_estale()` permits.

State and persistence: lookup state is transient path, dentry, mount, filename, qstr, and rename state. Persistent effects happen only when callers proceed into VFS create/remove/rename operations after setup; this header defines the coordination contract rather than storage.

Dependencies and integration points: depends on VFS core types, paths, fcntl flags, errno, fs_struct, idmapped mounts, dentries, and current umask. It is a central integration point between syscalls, filesystems, automount/mount traversal, security/perms, and scoped path resolution such as openat2-style containment.

Risks and test signals: risks include incorrect lookup flag combinations, accidentally following symlinks/magic links/mounts under scoped lookups, missing `end_*()` cleanup on error, holding or dropping dentries incorrectly, umask stripping divergence for POSIX ACL filesystems, and failing to retry `-ESTALE` with `LOOKUP_REVAL`. Test symlink depth, RCU versus ref pathwalk fallbacks, automount and mount crossing, `LOOKUP_BENEATH`/`LOOKUP_IN_ROOT` escape attempts, create/remove/rename races, network filesystem stale dentries, and POSIX ACL/no-umask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/namei.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nd.h -->
# sources/distributed-fs/ceph-client/include/linux/nd.h

Purpose: declares the kernel libnvdimm/NVDIMM device model interfaces for namespace devices, driver registration, region notifications, raw namespace byte I/O, claim classes, and optional NVDIMM perf PMU support.

Important APIs and types: enums `nvdimm_event` and `nvdimm_claim_class` classify revalidation events and namespace ownership personalities such as BTT, PFN, and DAX. PMU macros and `struct nvdimm_pmu` support NVDIMM performance counters when `CONFIG_PERF_EVENTS` is enabled, with stubs returning `-ENXIO` otherwise. `struct nd_device_driver` wraps a `device_driver` with type, probe/remove/shutdown, and event notify callbacks. `struct nd_namespace_common` embeds the namespace device, claim owner/class, force-raw flag, and `rw_bytes` callback. `struct nd_namespace_io` adds a resource, cached size, direct address, and badblocks. `struct nd_namespace_pmem` adds block-sector size, label/UUID, and id. Helpers include `to_ndns()`, `to_nd_namespace_io()`, `to_nd_namespace_pmem()`, `nvdimm_read_bytes()`, `nvdimm_write_bytes()`, module aliases, `nvdimm_region_notify()`, `__nd_driver_register()`, `nd_driver_unregister()`, `nd_driver_register()`, and `module_nd_driver()`.

Control flow: libnvdimm creates namespace devices and drivers register typed `nd_device_driver` instances. Drivers probe namespace devices, may claim them for BTT/PFN/DAX personalities, perform byte-granular reads/writes through `rw_bytes`, receive poison/region revalidation events, and unregister through the normal driver model. PMU users register an NVDIMM PMU with platform device context when perf support is available.

State and persistence: namespace objects represent persistent memory ranges, including resource address/size, optional labels/UUIDs, badblock tracking, and claim ownership. The header-owned structures are kernel object state; backing contents are persistent NVDIMM media, and write durability depends on namespace driver flushing behavior.

Dependencies and integration points: depends on fs/device/resource types, ndctl UAPI constants, badblocks, perf events, platform devices, UUIDs, and module registration. It integrates ACPI NFIT/platform NVDIMM discovery, block/DAX personalities, badblock/poison handling, perf counters, and driver-model matching via `nd:t%d` aliases.

Risks and test signals: risks include assuming `nvdimm_write_bytes()` guarantees media persistence, claim-class conflicts, badblock range mismatch, force-raw bypassing higher-level personalities, PMU CPU hotplug handling, and stale namespace labels. Test namespace probe/remove, raw byte I/O with flags, BTT/PFN/DAX claim transitions, poison revalidation, badblock reporting, perf PMU register/unregister with CPU hotplug, and builds without `CONFIG_PERF_EVENTS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ndctl.h -->
# sources/distributed-fs/ceph-client/include/linux/ndctl.h

Purpose: kernel wrapper around the NVDIMM control UAPI that defines common in-kernel constants.

Important APIs and types: includes `uapi/linux/ndctl.h` and defines `ND_MIN_NAMESPACE_SIZE` as `PAGE_SIZE`.

Control flow: NVDIMM/libnvdimm code includes this header to access ndctl UAPI definitions and the minimum namespace-size constraint during namespace creation or validation.

State and persistence: no state is owned here. The size constant affects validation of persistent namespace configuration.

Dependencies and integration points: depends on ndctl UAPI and `PAGE_SIZE` availability through kernel includes. It bridges ioctl/control-plane definitions into kernel NVDIMM code.

Risks and test signals: risks include accepting namespaces smaller than a page if callers bypass the constant, or architecture page-size changes affecting namespace minimums. Test namespace create/resize validation around `PAGE_SIZE` and compile users of ndctl UAPI definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ndctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net.h -->
# sources/distributed-fs/ceph-client/include/linux/net.h

Purpose: defines the kernel's central socket-layer interface: socket types and flags, socket wait queues, `struct socket`, protocol operation tables, protocol-family registration, socket creation/release, kernel send/receive helpers, rate-limited network logging, and sendpage safety checks.

Important APIs and types: `sockopt_t` wraps input/output `iov_iter`s and option length for type-safe sockopt handling. `enum socket_flags`, socket type constants, `SOCK_TYPE_MASK`, `SOCK_CLOEXEC`, `SOCK_NONBLOCK`, and shutdown commands define common socket behavior. `struct socket_wq` contains a wait queue, fasync list, RCU-protected flags, and RCU head. `struct socket` holds state, type, flags, backing file, protocol `sock`, mutable `proto_ops`, and wait queue. `struct proto_ops` is the full protocol method table for release, bind, connect, accept, getname, poll, ioctls, timestamping, listen, shutdown, sockopts, fdinfo, sendmsg/recvmsg, mmap/splice, peek, locked read/send helpers, and buffer tuning. `struct net_proto_family` registers address families. Public APIs include `sock_register()`, `sock_unregister()`, `__sock_create()`, `sock_create*()`, `sock_alloc()`, `sock_release()`, `sock_sendmsg()`, `sock_recvmsg()`, `sock_alloc_file()`, `sockfd_lookup()`, `sock_from_file()`, `kernel_*()` socket operations, `kernel_sock_ip_overhead()`, and module alias macros.

Control flow: address-family providers register a `net_proto_family`; socket creation allocates a `struct socket` and calls the family `create()` to install protocol operations and a `struct sock`. File-descriptor users call through VFS into `proto_ops`, while in-kernel users call `kernel_sendmsg()`, `kernel_recvmsg()`, `kernel_bind()`, `kernel_connect()`, and related helpers. Wait queues and async flags drive poll/fasync notifications. `sendpage_ok()`/`sendpages_ok()` reject slab or unreferenced pages before zero-copy page transmission.

State and persistence: socket state is in-memory and lifetime-bound to the file/socket reference count: connection state, wait queue flags, protocol private state in `sk`, and mutable operation tables for protocol transitions. No durable state is stored, but sockets carry live network connections and kernel/user references.

Dependencies and integration points: depends on fs, mm, RCU, wait queues, fasync, sockptr, UIO/iov_iter, UAPI socket definitions, modules, sk_buffs, files, pipes, pages, and network namespaces. It is the integration boundary between VFS descriptors, protocol families, transport implementations, kernel networking clients, dynamic debug, and module autoload aliases.

Risks and test signals: risks include protocol ops missing required callbacks, wrong `msg_namelen` handling in recvmsg, stale RCU wait-queue flags, leaking socket file references after `sockfd_lookup()`, unsafe sendpage on slab/high-order pages, incompatible compat ioctls, and mutable `ops` transitions such as MPTCP or IPv6 addrform. Test protocol family register/unregister, socket create/release errors, poll/fasync wakeups, kernel send/recv/connect/accept, sockopt iter paths, timestamp ioctl paths, sendpage safety on slab and compound pages, and module alias autoloading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/i40e_client.h -->
# sources/distributed-fs/ceph-client/include/linux/net/intel/i40e_client.h

Purpose: defines the client interface between the Intel i40e LAN driver and auxiliary clients such as iWARP/RDMA consumers.

Important APIs and types: version macros and `struct i40e_client_version` identify the interface. `struct i40e_qv_info` and flexible `struct i40e_qvlist_info` describe MSI-X vector to CEQ/AEQ/ITR mappings. QoS types `i40e_prio_qos_params`, `i40e_qos_params`, and `i40e_params` expose priority-to-traffic-class and MTU information. `struct i40e_info` describes a LAN device to clients: MAC, netdev, PCI device, auxiliary device, MMIO base, function id/type, PF private pointer, qvector list, mutable L2 params, operations, MSI-X entries, ITR index, and firmware version. `struct i40e_ops` lets clients set qvector lists, send virtchnl messages, request PF/core resets, and update VSI context flags. `struct i40e_client_ops` lets the LAN driver open/close clients, notify L2 param changes, deliver virtchnl messages, signal VF resets/enables, and query VF offload capability. `struct i40e_client_instance` and `struct i40e_client` track registered clients, state, refcount, flags, type, and ops.

Control flow: an i40e client registers with the LAN driver, which creates client instances for ready LAN devices and calls `open()`. The client requests queue/vector setup, sends or receives virtchnl traffic, receives MTU/QoS/VF/reset notifications, and calls reset/update hooks as needed. On netdev removal, reset, or client unregister, `close()` is invoked and `i40e_client_device_unregister()` tears down the association.

State and persistence: state is runtime coordination state: client lists, per-instance open state, refcounts, qvector allocations, MSI-X entries, L2 parameters, and firmware version snapshots. There is no persistent state; hardware configuration effects are mediated by i40e.

Dependencies and integration points: depends on auxiliary bus, netdev, PCI/MSI-X, MMIO, virtchnl messaging, and i40e PF internals. It bridges Ethernet PF ownership with RDMA/PE-engine style clients.

Risks and test signals: risks include interface version mismatch, qvector flexible-array sizing errors, stale `netdev` or `pcidev` during reset, failing to close on unregister, virtchnl message length validation, VF id misuse, and inconsistent QoS/MTU notifications. Test client register/unregister, PF reset and core reset, MTU change callbacks, VF enable/reset/capability paths, qvector setup with invalid indices, and concurrent netdev removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/i40e_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma.h -->
# sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma.h

Purpose: declares the common Intel IIDC RDMA auxiliary-device interface shared between LAN PCI drivers and RDMA auxiliary drivers.

Important APIs and types: `enum iidc_rdma_event_type` defines MTU, traffic-class, reset warning, and critical-error event bits. `struct iidc_rdma_event` carries a bitmap of event types plus a register value. Reset types distinguish function and device reset, while protocol bits identify iWARP and RoCEv2. `struct iidc_rdma_core_dev_info` carries the PCI device, auxiliary device, active RDMA protocol, and driver-private IIDC data. `struct iidc_rdma_core_auxiliary_dev` embeds an auxiliary device with core info. `struct iidc_rdma_core_auxiliary_drv` embeds an auxiliary driver and an event handler.

Control flow: the LAN core allocates/populates core device info and auxiliary devices; the RDMA auxiliary driver binds through auxiliary bus registration and receives event callbacks for MTU/TC changes and reset/error conditions. Driver-specific headers extend the common core info with LAN-specific operations.

State and persistence: state is live device association and selected RDMA protocol. There is no durable storage; resets and events describe transient hardware/software state.

Dependencies and integration points: depends on auxiliary bus, PCI/device/netdevice headers, Ethernet constants, kernel bitmap helpers, and DSCP definitions. It forms the common IIDC handshake between Intel LAN drivers and RDMA providers.

Risks and test signals: risks include event bitmap width drift, stale auxiliary device lifetime, mismatched active protocol, null private data expectations, and event ordering around MTU/TC before/after notifications. Test auxiliary probe/remove, protocol selection, before/after MTU and TC events, warning and critical reset paths, and multi-protocol compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma_ice.h -->
# sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma_ice.h

Purpose: extends the common IIDC RDMA interface with ICE-specific queue-set, QoS, VSI filter, reset, and MSI-X vector allocation APIs.

Important APIs and types: constants define maximum user priorities and DSCP PFC mode. `struct iidc_rdma_qset_params` carries TEID, RDMA-provided queue-set handle, vport id, and traffic class. `struct iidc_rdma_qos_info` and `struct iidc_rdma_qos_params` expose per-TC context, relative bandwidth, priority type, virtual user priorities, UP-to-TC map, vport scheduling settings, TC count, PFC mode, and DSCP map. `struct iidc_rdma_priv_dev_info` provides PF id, vport id, netdev, QoS info, and MMIO base. ICE callbacks include `ice_add_rdma_qset()`, `ice_del_rdma_qset()`, `ice_rdma_request_reset()`, `ice_rdma_update_vsi_filter()`, `ice_alloc_rdma_qvector()`, and `ice_free_rdma_qvector()`.

Control flow: an RDMA driver receives ICE private device info, allocates vectors, adds qsets to traffic classes, enables VSI filtering, reacts to QoS changes from IIDC events, and removes qsets/vectors during teardown. Reset requests are sent back to ICE using function or device reset types from the common header.

State and persistence: runtime state includes qset TEIDs returned by ICE, MSI-X vector reservations, vport/QoS snapshots, filters, and MMIO access. No state is persistent outside hardware configuration and driver-owned objects.

Dependencies and integration points: depends on DCBNL TC constants, DSCP sizing from the common include stack, netdev, MSI-X, MMIO, and ICE LAN driver internals. It connects RDMA scheduling and filtering to ICE's LAN resource manager.

Risks and test signals: risks include stale TEID use after qset deletion, TC/UP/DSCP map mismatch, vector leaks, enabling filters on wrong VSI, reset request escalation, and QoS array bounds over `IEEE_8021QAZ_MAX_TCS` or DSCP_MAX. Test qset add/delete, vector allocate/free, MTU/TC/QoS changes, VSI filter enable/disable, reset requests, PFC/DSCP modes, and teardown after partial allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma_ice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma_idpf.h -->
# sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma_idpf.h

Purpose: extends the common IIDC RDMA model for IDPF-managed vports, mapped memory regions, function type reporting, vport control, reset requests, and synchronous virtchnl messaging.

Important APIs and types: `struct iidc_rdma_vport_dev_info` connects a vport auxiliary device to the core auxiliary device, netdev, and vport id. `struct iidc_rdma_vport_auxiliary_dev` and `struct iidc_rdma_vport_auxiliary_drv` wrap auxiliary bus objects and vport event handling. `enum iidc_function_type` distinguishes PF and VF. `struct iidc_rdma_lan_mapped_mem_region` describes MMIO region address, size, and start offset. `struct iidc_rdma_priv_dev_info` exposes reserved MSI-X entries/count, function type, number of mapped memory regions, and the region array. Functions include `idpf_idc_vport_dev_ctrl()`, `idpf_idc_request_reset()`, and `idpf_idc_rdma_vc_send_sync()`.

Control flow: IDPF creates core and vport auxiliary devices; an RDMA vport driver binds, uses private info for MSI-X and mapped memory, controls vport up/down state, sends synchronous virtchnl messages, and receives vport events through its auxiliary driver handler. Reset requests are routed through IDPF's IDC hooks.

State and persistence: state is runtime auxiliary-device linkage, vport id, reserved interrupts, mapped LAN memory windows, and virtchnl exchange buffers. No durable state is owned here.

Dependencies and integration points: depends on auxiliary bus, netdev/MSI-X types from the common include stack, endian types, and IDPF IDC/virtchnl implementation. It integrates RDMA auxiliary drivers with IDPF's split core/vport device model.

Risks and test signals: risks include vport/core auxiliary lifetime races, incorrect `num_memory_regions` endian handling, mapped region bounds mistakes, synchronous virtchnl buffer length errors, reserved MSI-X leaks, and PF/VF behavior divergence. Test vport auxiliary probe/remove, up/down control, reset request behavior, virtchnl send/receive length handling, mapped memory enumeration, and PF/VF configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma_idpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/libie/adminq.h -->
# sources/distributed-fs/ceph-client/include/linux/net/intel/libie/adminq.h

Purpose: defines Intel libie Admin Queue descriptor formats, command parameter structures, capability identifiers, firmware logging opcodes, descriptor flags, firmware return codes, and helpers shared by Intel Ethernet drivers.

Important APIs and types: `LIBIE_CHECK_STRUCT_LEN()` statically enforces wire-format structure sizes, and `LIBIE_AQ_MAX_BUF_LEN` caps indirect buffers. Command parameter structs include `libie_aqc_generic`, `libie_aqc_get_ver`, `libie_aqc_driver_ver`, `libie_aqc_req_res`, `libie_aqc_list_caps`, `libie_aqc_list_caps_elem`, `libie_aqc_fw_log`, and `libie_aqc_fw_log_cfg_resp`. Resource enums define NVM/SDP/change/global locks, access types, timeouts, and global lock status. Capability macros enumerate switch, management, SR-IOV, VF/VMDQ/VSI/DCB/FCoE/iSCSI/RSS/RXQ/TXQ/MSI-X/1588/MTU/NVM/RDMA/LED/MDIO/security/topology/LAG and related features. `enum libie_adminq_opc` defines firmware logging opcodes. Firmware logging modules and flags configure/query/register logs. `struct libie_aq_desc` is the 32-byte descriptor with flags, opcode, datalen, retval, cookies, and a 16-byte params union. Descriptor flag macros define DD/CMP/ERR/VFE/LB/RD/VFC/BUF/SI/EI/FE. `enum libie_aq_err` maps firmware error return codes, `libie_aq_raw()` returns the raw params area, and `libie_aq_str()` converts errors to text.

Control flow: drivers fill a `libie_aq_desc` with opcode, flags, data length, cookies, and command-specific params, optionally point it at an indirect buffer, post it to the admin transmit queue, and inspect writeback flags/retval/params. Firmware asynchronous events arrive on the admin receive queue using the same descriptor format. Resource lock commands acquire/release shared firmware resources; capability commands parse indirect capability buffers; firmware logging commands configure and fetch log events.

State and persistence: descriptors and command buffers are transient DMA/adminq state. Resource ownership and firmware logging registration affect firmware-maintained runtime state; NVM/resource operations may protect persistent hardware contents but this header only defines protocol formats.

Dependencies and integration points: depends on build-time static assertions and little-endian fixed-width types. It integrates Intel Ethernet drivers with firmware AdminQ command ABI and is consumed by higher-level libie firmware logging and capability code.

Risks and test signals: risks include structure packing or endian mistakes, failing static size assertions, buffer lengths above `LIBIE_AQ_MAX_BUF_LEN`, wrong large-buffer flags for indirect commands, stale capability ids, unhandled firmware error codes, and resource lock timeout misuse. Test descriptor size assertions, get-version/send-driver-version, resource acquire/release timeout paths, capability parsing, firmware logging opcodes, endian conversion, and `libie_aq_str()` coverage for all enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/libie/adminq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/libie/fwlog.h -->
# sources/distributed-fs/ceph-client/include/linux/net/intel/libie/fwlog.h

Purpose: declares the libie firmware logging configuration, ring storage, debugfs/API context, and optional runtime functions for Intel Ethernet firmware log collection.

Important APIs and types: `enum libie_fwlog_level` defines none/error/warning/normal/verbose levels and an invalid sentinel. `struct libie_fwlog_module_entry` maps firmware module id to log level. `struct libie_fwlog_cfg` holds one entry per AdminQ firmware log module, option bits for ARQ, UART, register-on-init, and registered-state, plus log resolution. `struct libie_fwlog_data` stores one event buffer. `struct libie_fwlog_ring` tracks ring array, selected size index, total size, head, and tail. Ring-size constants define defaults and max. `struct libie_fwlog` contains config, support flag, ring, debugfs dentries, and grouped API fields: PCI device, AdminQ send callback, private pointer, and debugfs root. When `CONFIG_LIBIE_FWLOG` is enabled, functions include init/deinit/reregister/get-data; otherwise stubs return `-EOPNOTSUPP` or no-op.

Control flow: a driver initializes the API group with PCI/debugfs/AdminQ send context, sets desired config options, and calls `libie_fwlog_init()`. If supported and registered, firmware log events delivered over AdminQ/ARQ are copied into the ring; debugfs exposes module controls and data retrieval calls drain or copy log data. `libie_fwlog_reregister()` restores registration after resets.

State and persistence: state is in-memory configuration, support status, circular log buffers, and debugfs entries. Firmware registration is runtime hardware state; logs are diagnostic and not persistent unless userspace copies them.

Dependencies and integration points: depends on `libie/adminq.h`, PCI devices, debugfs, and a driver-provided AdminQ send function. It integrates firmware AdminQ log opcodes with debugfs and driver reset handling.

Risks and test signals: risks include accepting invalid log levels, ring head/tail wrap bugs, debugfs lifetime leaks, failing to reregister after reset, assuming support when firmware lacks logging, and disabled-config stubs hiding missing functionality. Test enabled/disabled `CONFIG_LIBIE_FWLOG`, init/deinit, module level changes, ARQ/UART option handling, ring wrap at max size, data retrieval length bounds, and reset reregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/libie/fwlog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/libie/pctype.h -->
# sources/distributed-fs/ceph-client/include/linux/net/intel/libie/pctype.h

Purpose: defines Intel packet classifier type identifiers used for RSS hash enable registers and virtchnl RSS hash configuration.

Important APIs and types: `enum libie_filter_pctype` assigns hardware packet-class values for non-fragmented IPv4/IPv6 UDP/TCP/SCTP/other, TCP SYN without ACK, fragmented IPv4/IPv6, FCoE classes, and L2 payload. Comments document reserved ranges and values unsupported on XL710/X710.

Control flow: drivers use these enum values when programming HENA/register bits or communicating RSS hash capabilities over virtchnl. The numeric values must match hardware/firmware definitions.

State and persistence: no state is kept. The constants configure hardware hashing/classification state elsewhere.

Dependencies and integration points: no external includes beyond the guard. Integrates Intel Ethernet hardware packet classification with driver and virtchnl control paths.

Risks and test signals: risks include changing numeric values, enabling unsupported PCTYPEs on older devices, and mismatching RSS hash fields with classifier type. Test RSS hash enable programming, virtchnl capability exchange, old XL710/X710 device behavior, and packet-flow classification for IPv4, IPv6, FCoE, fragments, and L2 payload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/libie/pctype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/libie/rx.h -->
# sources/distributed-fs/ceph-client/include/linux/net/intel/libie/rx.h

Purpose: provides Intel Ethernet receive buffer/frame sizing constants and a safe wrapper for converting hardware packet types into parsed libeth RX packet-type metadata.

Important APIs and types: `LIBIE_MAX_RX_BUF_LEN` is the hardware maximum per descriptor, `LIBIE_RX_BUF_LEN(hr)` clamps libeth page length by headroom to hardware max, `__LIBIE_MAX_RX_FRM_LEN` is the hardware scatter/gather frame limit, `LIBIE_MAX_RX_FRM_LEN(hr)` clamps chained descriptor frame length, and `LIBIE_MAX_MTU` subtracts link-layer overhead. `LIBIE_RX_PT_NUM` sizes the packet-type lookup table. `libie_rx_pt_lut[]` is the external parsed packet-type table, and `libie_rx_pt_parse()` bounds-checks a 10-bit hardware packet type, maps out-of-range values to zero, and returns `struct libeth_rx_pt`.

Control flow: RX descriptor handling reads the hardware packet type and calls `libie_rx_pt_parse()` instead of indexing the LUT directly. Buffer sizing macros are used during RX ring setup and MTU validation to choose hardware-writable buffer sizes and maximum frame limits.

State and persistence: no mutable state is owned here; the lookup table is static read-only data defined elsewhere. Runtime RX rings and buffers live in drivers/libeth.

Dependencies and integration points: depends on `net/libeth/rx.h` for headroom, link-layer length, and parsed packet-type definitions. It connects Intel i40e/ice/iavf-style packet type encodings with shared libeth RX parsing.

Risks and test signals: risks include direct LUT indexing without bounds checks, MTU calculations drifting from descriptor-chain limits, headroom-dependent buffer underestimation, and packet-type table mismatch with hardware. Test out-of-range packet types, every valid LUT entry, max MTU validation, RX buffer sizing with different headroom, jumbo frames, and chained descriptor receive paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net/intel/libie/rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net_tstamp.h -->
# sources/distributed-fs/ceph-client/include/linux/net_tstamp.h

Purpose: defines in-kernel hardware timestamp provider metadata and an extensible kernel timestamp configuration wrapper around the UAPI `hwtstamp_config`.

Important APIs and types: software and hardware timestamping masks group the relevant `SOF_TIMESTAMPING_*` bits. `struct hwtstamp_provider_desc` carries provider index and qualifier. `struct hwtstamp_provider` is RCU-freed provider state with source, optional PHY device pointer, and descriptor. `struct kernel_hwtstamp_config` extends UAPI flags/tx_type/rx_filter with the original `ifreq`, copied-to-user marker for legacy lower drivers, timestamp source, and provider qualifier. Helpers copy config to/from UAPI form and compare whether flags/tx/rx fields changed.

Control flow: ioctl/netdev timestamp configuration code copies userspace `hwtstamp_config` into `kernel_hwtstamp_config`, augments it with source/provider information, may pass the original ifreq to legacy lower drivers, and copies the result back if needed. Provider objects can represent netdev or PHY timestamp sources and are released through RCU.

State and persistence: timestamp configuration is runtime netdev/PHY state. Provider objects are in-memory and RCU-managed; no durable state is owned by the header.

Dependencies and integration points: depends on timestamping UAPI and generated ethtool netlink enums. It integrates SIOCG/SIOCSHWTSTAMP, netdev timestamp providers, phylib PTP timestamping, ethtool netlink reporting, and legacy driver ioctl paths.

Risks and test signals: risks include losing extended source/qualifier state when converting to UAPI, double-copying ioctl data when `copied_to_user` is set, RCU lifetime bugs for providers, and failing to detect meaningful config changes. Test netdev versus PHY timestamp providers, legacy lower-driver ioctl handoff, ethtool provider reporting, config compare paths, RCU teardown, and software/hardware timestamp mask combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/net_tstamp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netdev_features.h -->
# sources/distributed-fs/ceph-client/include/linux/netdev_features.h

Purpose: defines the 64-bit network-device feature bit namespace, feature constants, iteration helpers, and masks used by netdev, ethtool, virtual devices, VLAN/tunnel stacks, checksum/GSO/GRO, and hardware offload negotiation.

Important APIs and types: `netdev_features_t` is `u64`. The feature enum assigns bit positions for scatter-gather, IPv4/IPv6/all checksum offload, high DMA, fraglists, VLAN CTAG/STAG TX/RX/filter, GSO/GRO/LRO, all GSO subtypes from TSO through AccECN, FCoE/SCTP CRC, ntuple, RX hash/checksum/FCS/all, loopback, L2 forwarding offload, TC, ESP/TLS/MACsec/HSR hardware offloads, UDP tunnel ports, GRO fraglist/UDP forwarding, and `NETDEV_FEATURE_COUNT`. `__NETIF_F_BIT()` and `__NETIF_F()` build masks, with one macro per feature. `find_next_netdev_feature()` and `for_each_netdev_feature()` iterate set bits from high to low. Masks include `NETIF_F_NEVER_CHANGE`, `NETIF_F_ETHTOOL_BITS`, `NETIF_F_GSO_MASK`, `NETIF_F_CSUM_MASK`, `NETIF_F_ALL_TSO`, `NETIF_F_GSO_SOFTWARE`, `NETIF_F_ONE_FOR_ALL`, `NETIF_F_ALL_FOR_ALL`, `NETIF_F_UPPER_DISABLES`, `NETIF_F_SOFT_FEATURES`, VLAN/GSO-encap and master-upper feature masks. `netdev_base_features()` normalizes aggregate feature sets.

Control flow: drivers declare supported, wanted, VLAN, hardware encapsulation, and active feature masks using these bits. Core netdev and ethtool code validate user changes, combine lower-device features into upper devices, disable incompatible features, and iterate masks to display or reconcile capabilities. GSO bit ordering is intentionally aligned with `SKB_GSO_*` bits.

State and persistence: feature masks are in-memory per-netdev capability/configuration state. Some bits cause hardware programming, but this header only defines bit positions and policy masks.

Dependencies and integration points: depends on generic bit operations, fixed-width types, and byteorder. It integrates with ethtool strings, `Documentation/networking/netdev-features.rst`, SKB GSO types, VLAN/tunnel/master devices, hardware offload drivers, and userspace feature toggles.

Risks and test signals: risks include exceeding 64 feature bits, changing enum order and breaking SKB GSO alignment or userspace expectations, not updating ethtool string tables/docs, contradictory checksum bits (`HW_CSUM` with IP/IPV6), incorrect upper/lower feature propagation, and offloads enabled without hardware support. Test ethtool feature toggles, feature iteration boundaries, GSO/GRO/checksum/VLAN/tunnel aggregation, virtual upper-device feature inheritance, all offload masks, and compile-time review when adding new bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/netdev_features.h -->
