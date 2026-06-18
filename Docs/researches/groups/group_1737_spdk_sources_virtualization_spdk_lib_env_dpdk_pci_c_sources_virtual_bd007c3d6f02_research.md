# Group Research: group_1737_spdk_sources_virtualization_spdk_lib_env_dpdk_pci_c_sources_virtual_bd007c3d6f02

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/pci.c

Implements SPDK's DPDK-backed PCI environment layer. It owns global PCI driver/device/provider registries, maps DPDK `rte_pci_device` objects into `spdk_pci_device`, and provides SPDK-facing APIs for enumeration, explicit attach/detach, BAR mapping, config-space access, interrupts, claims, address parsing/formatting, and device allowlisting.

Important behavior:
- Maintains `g_pci_devices`, `g_pci_hotplugged_devices`, `g_pci_drivers`, and `g_pci_device_providers` under `g_pci_mutex`.
- Uses delayed `rte_devargs` allow/block policy to avoid immediately probing newly seen devices during scans.
- Handles DPDK hotplug remove events with deferred alarm callbacks and `pending_removal`/`removed` state.
- Registers SPDK PCI drivers with DPDK through the compatibility wrappers from `pci_dpdk.h`.
- For VFIO/IOMMU builds, maps BAR memory into the IOMMU on `spdk_pci_device_map_bar()` and unmaps on BAR unmap.
- Linux claim/unclaim uses `/var/tmp/spdk_pci_lock_<bdf>` files plus `fcntl` locks and stored PID.

Filesystem/storage relevance: this is the low-level device discovery and lifetime layer for SPDK PCI-backed storage devices such as NVMe, IOAT/IDXD DMA engines, VMD, and virtio block/SCSI.

Concurrency and lifecycle notes:
- `spdk_pci_device_detach()` clears attachment, calls the provider detach callback, and then cleans removed/hotplugged queues.
- `spdk_pci_enumerate()` first enumerates known unattached devices, then scans/probes the DPDK bus, then cleans hotplug results.
- `pci_env_fini()` only reports devices still attached; it does not forcibly detach them.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_ae4dma.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_ae4dma.c

Registers the AMD AE4DMA PCI driver with SPDK's PCI layer.

Important behavior:
- Defines an AMD-vendor PCI ID table for `PCI_DEVICE_ID_AMD_AE4DMA_3E` and `PCI_DEVICE_ID_AMD_AE4DMA_4E`.
- Exposes `spdk_pci_ae4dma_get_driver()` as a typed accessor around `spdk_pci_get_driver("ae4dma")`.
- Uses `SPDK_PCI_DRIVER_REGISTER(ae4dma, ..., SPDK_PCI_DRIVER_NEED_MAPPING)`.

Filesystem/storage relevance: provides discovery for AMD DMA accelerator devices that SPDK components may use for offloaded data movement.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_ae4dma.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk.c

Provides the public wrapper layer over DPDK PCI/private-ABI access. It selects a version-specific function table at runtime based on `rte_version()` and forwards all PCI/device/bus operations through that table.

Important behavior:
- Supports DPDK 21.11+ through selected 22.07 or 22.11 compatibility tables.
- Maps DPDK 22.11 ABI implementation to later supported 23.x, 24.x, 25.x, and 26.03 releases when the private ABI is considered unchanged.
- Rejects unsupported DPDK versions with `-EINVAL`.
- Wraps mem resources, device names/devargs/address/ID/NUMA, config read/write, driver registration, interrupts, bus scan/probe, and generic device devargs/name/scan-allowed helpers.

Dependency boundary: this file prevents the rest of SPDK env PCI code from directly depending on a specific DPDK private struct layout.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk.h -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk.h

Declares SPDK's DPDK PCI compatibility interface.

Important contents:
- `struct spdk_pci_driver` embeds a fixed `driver_buf[256]` for an `rte_pci_driver`, then stores SPDK driver metadata and enumeration callback state.
- `struct dpdk_fn_table` defines all DPDK ABI-sensitive operations used by `pci.c`.
- Declares wrappers for DPDK PCI resources, config access, interrupt setup, bus scan/probe, and generic device devargs operations.

Risk note: the fixed-size `driver_buf` is guarded by static assertions in version-specific implementation files, so compatibility depends on those assertions matching the selected DPDK headers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk_2207.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk_2207.c

Implements `dpdk_fn_table` for DPDK 22.07-style private PCI structures.

Important behavior:
- Includes DPDK 22.07 private compatibility headers.
- Static-asserts that `spdk_pci_driver.driver_buf` starts at offset 0 and is large enough for `struct rte_pci_driver`.
- Directly accesses `rte_pci_device` fields such as `mem_resource`, `name`, `device.devargs`, `addr`, `id`, `device.numa_node`, and `intr_handle`.
- Converts SPDK PCI ID tables into DPDK `rte_pci_id` arrays and registers with `rte_pci_register()`.
- Translates SPDK driver flags to `RTE_PCI_DRV_NEED_MAPPING` and `RTE_PCI_DRV_WC_ACTIVATE`.
- Provides interrupt helpers around `rte_intr_*`.

Compatibility role: selected by `pci_dpdk.c` for older supported DPDK versions whose private PCI ABI matches this layout.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk_2207.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk_2211.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk_2211.c

Implements `dpdk_fn_table` for DPDK 22.11-style private PCI structures.

Important behavior:
- Includes 22.11 private bus/PCI driver headers.
- Mirrors the 22.07 implementation for resource lookup, device metadata, config read/write, driver registration, interrupt operations, and bus/device helpers.
- Defines compile-time traps for newer APIs such as `rte_pci_mmio_read`, `rte_pci_mmio_write`, and `rte_pci_pasid_set_state`, requiring a new compat layer if SPDK begins using them.
- Used by `pci_dpdk.c` for DPDK 22.11 and later versions deemed ABI-compatible.

Compatibility role: this is the primary function table for modern supported DPDK versions in this source snapshot.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_dpdk_2211.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_event.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_event.c

Implements Linux PCI uevent listening and parsing for SPDK.

Important behavior:
- On Linux, opens a nonblocking `NETLINK_KOBJECT_UEVENT` socket subscribed to all groups.
- Attempts to set a 1 MiB receive buffer with `SO_RCVBUFFORCE` or `SO_RCVBUF`.
- Parses UIO `add`/`remove` events by extracting the PCI BDF from `DEVPATH`.
- Parses VFIO add events from `ACTION=bind`, `DRIVER=vfio-pci`, and `PCI_SLOT_NAME`.
- Fills `struct spdk_pci_event` with `SPDK_UEVENT_ADD` or `SPDK_UEVENT_REMOVE` plus parsed PCI address.
- Non-Linux builds return `-ENOTSUP`.

Integration note: VFIO hotremove itself is handled through DPDK callbacks in `pci.c`; this file mainly supports device add/allow notification paths.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_event.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_idxd.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_idxd.c

Registers Intel IDXD/DSA/IAA devices with SPDK's PCI layer.

Important behavior:
- Defines Intel-vendor IDs for DSA, DSA3, IAA, and IAA3 devices.
- Exposes `spdk_pci_idxd_get_driver()` around `spdk_pci_get_driver("idxd")`.
- Registers with `SPDK_PCI_DRIVER_NEED_MAPPING`.

Filesystem/storage relevance: IDXD devices can accelerate data movement and checksum/copy paths used by SPDK storage services.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_idxd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_ioat.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_ioat.c

Registers Intel IOAT DMA engine PCI IDs with SPDK.

Important behavior:
- Contains a broad Intel IOAT ID table spanning SNB, IVB, HSW, BWD, BDX, SKX, and ICX device IDs.
- Exposes `spdk_pci_ioat_get_driver()` around `spdk_pci_get_driver("ioat")`.
- Registers the driver with `SPDK_PCI_DRIVER_NEED_MAPPING`.

Filesystem/storage relevance: IOAT devices are DMA offload engines used by SPDK for copy/data-movement acceleration.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_ioat.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_virtio.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_virtio.c

Registers virtio PCI storage device IDs with SPDK.

Important behavior:
- Matches modern and legacy virtio SCSI and virtio block PCI IDs.
- Exposes `spdk_pci_virtio_get_driver()` around `spdk_pci_get_driver("virtio")`.
- Registers with both `SPDK_PCI_DRIVER_NEED_MAPPING` and `SPDK_PCI_DRIVER_WC_ACTIVATE`.

Filesystem/storage relevance: enables SPDK virtio block/SCSI devices in virtualized environments.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_virtio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_vmd.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/pci_vmd.c

Registers Intel VMD PCI controller IDs with SPDK.

Important behavior:
- Matches Intel SKX and ICX VMD device IDs.
- Exposes `spdk_pci_vmd_get_driver()` around `spdk_pci_get_driver("vmd")`.
- Registers with `SPDK_PCI_DRIVER_NEED_MAPPING | SPDK_PCI_DRIVER_WC_ACTIVATE`.

Filesystem/storage relevance: VMD is commonly used to expose/manage NVMe devices behind Intel Volume Management Device controllers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/pci_vmd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/sigbus_handler.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/sigbus_handler.c

Provides a global SIGBUS dispatch mechanism for PCI error handlers.

Important behavior:
- Installs a `SIGBUS` `sigaction` handler at library constructor time.
- Maintains a mutex-protected tail queue of registered `spdk_pci_error_handler` callbacks.
- On SIGBUS, calls each registered callback with `info->si_addr` and the callback context.
- Prevents duplicate registration by function pointer.
- Frees handler records at destructor time.

Risk note: the signal handler locks a pthread mutex and calls arbitrary callbacks, which is not async-signal-safe in strict POSIX terms; this is an SPDK-specific fault-dispatch mechanism.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/sigbus_handler.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/threads.c -->
# File Research: sources/virtualization/spdk/lib/env_dpdk/threads.c

Maps SPDK environment core/thread APIs onto DPDK lcore APIs.

Important behavior:
- Core queries wrap `rte_lcore_count`, `rte_lcore_id`, `rte_get_main_lcore`, and `rte_get_next_lcore`.
- NUMA queries wrap DPDK socket APIs.
- `spdk_env_get_cpuset()` builds an SPDK cpuset from active DPDK lcores.
- Linux SMT sibling discovery reads `/sys/devices/system/cpu/cpu%d/topology/thread_siblings` and parses it as an SPDK cpuset.
- Thread launch/wait use `rte_eal_remote_launch()` and `rte_eal_mp_wait_lcore()`.

Integration note: this file is the env layer that the event/reactor code uses to enumerate and launch one reactor per selected lcore.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_dpdk/threads.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/Makefile -->
# File Research: sources/virtualization/spdk/lib/env_ocf/Makefile

Builds the SPDK OCF environment library `ocfenv`.

Important behavior:
- Uses `CONFIG_OCF_DIR`/`CONFIG_OCF_PATH` to integrate Open CAS Framework sources.
- If `CONFIG_CUSTOMOCF=y`, copies a prebuilt OCF library into the SPDK static library path.
- Otherwise invokes the OCF make targets to export headers and sources into `lib/env_ocf`, then builds local C sources.
- `clean` removes exported OCF `include` and `src` directories plus generated objects/library.
- `exportlib` copies the built library to a caller-provided `O=` path.

Role: bridges SPDK's build system with either OCF source builds or precompiled OCF artifacts.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/mpool.c -->
# File Research: sources/virtualization/spdk/lib/env_ocf/mpool.c

Implements OCF-style multi-size memory pools using SPDK-backed `env_allocator` objects.

Important behavior:
- `env_mpool_create()` creates allocators for powers-of-two item counts from 1 through the configured max order.
- Each pool element size is `hdr_size + elem_size * (1 << i)`.
- Optional per-pool limits and zeroing are passed through to `env_allocator_create_extended()`.
- `env_mpool_get_allocator()` rounds requested count up to the appropriate power-of-two allocator.
- `env_mpool_new()` allocates from the matching allocator or falls back to `env_vmalloc()` when enabled.
- `env_mpool_del()` returns objects to the matching allocator or frees fallback allocations.

Risk note: deallocation requires the same `count` classification used at allocation time; otherwise the object may be returned to the wrong backing pool.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/mpool.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/mpool.h -->
# File Research: sources/virtualization/spdk/lib/env_ocf/mpool.h

Declares the OCF environment multi-pool API.

Important contents:
- Defines allocation orders `env_mpool_1` through `env_mpool_128`.
- Forward-declares `struct env_mpool`.
- Declares create/destroy/new/delete operations.
- `env_mpool_create()` accepts fixed header size, per-element size, max order, fallback mode, per-order limits, name prefix, and zeroing flag.

Note: the parameter name is spelled `name_perfix` in the declaration, while the implementation uses `name_prefix`; this is harmless C API spelling drift.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/mpool.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/ocf_env.c -->
# File Research: sources/virtualization/spdk/lib/env_ocf/ocf_env.c

Implements non-inline pieces of the OCF userspace environment on top of SPDK.

Important behavior:
- `env_allocator_*` wraps `spdk_mempool_create/get/put/free`.
- Allocator names are qualified with a global atomic index to keep names unique.
- Default allocator depth is `16383` objects unless a custom limit is supplied.
- Destroy checks that all objects were returned before freeing the mempool.
- `env_crc32()` delegates to `spdk_crc32_ieee_update()`.
- Execution-context emulation allocates one pthread mutex per online CPU at constructor time.
- `env_get_execution_context()` locks the current CPU's mutex based on `sched_getcpu()` and returns the CPU index; `env_put_execution_context()` unlocks it.

Compatibility role: supplies OCF with kernel-like allocator, CRC, and execution-context primitives in SPDK userspace.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/ocf_env.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/ocf_env.h -->
# File Research: sources/virtualization/spdk/lib/env_ocf/ocf_env.h

Defines the main OCF environment compatibility API for SPDK.

Important contents:
- Provides Linux-style scalar aliases, packed/aligned attributes, sector constants, `container_of`, `ARRAY_SIZE`, `min`, and logging/bug macros.
- Maps OCF allocation APIs to SPDK DMA-capable `spdk_malloc`, `spdk_zmalloc`, and `spdk_free`.
- Declares `env_allocator` and allocator functions implemented in `ocf_env.c`.
- Implements mutexes, recursive mutexes, rw semaphores, spinlocks, rwlocks, completions, waitqueues, atomics, and bit operations with pthreads, semaphores, and GCC sync builtins.
- Provides tick/time conversion wrappers over `spdk_get_ticks()` and `spdk_get_ticks_hz()`.
- Implements bounded memory/string helpers with OCF-style success/failure return conventions.
- Declares CRC and execution-context functions implemented externally.

Filesystem/storage relevance: this header is the main contract that allows OCF cache logic to compile and run inside SPDK's userspace environment.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/ocf_env.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/ocf_env_headers.h -->
# File Research: sources/virtualization/spdk/lib/env_ocf/ocf_env_headers.h

Small OCF environment header shim.

Important behavior:
- Includes `spdk/stdinc.h`.
- Defines OCF version macros: main `20`, major `3`, minor `0`.

Role: gives imported OCF code a stable environment/version header when compiled inside SPDK.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/ocf_env_headers.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/ocf_env_list.h -->
# File Research: sources/virtualization/spdk/lib/env_ocf/ocf_env_list.h

Implements a Linux-kernel-like intrusive doubly linked list API for OCF.

Important contents:
- Defines `struct list_head` aligned to 64 bytes.
- Implements `INIT_LIST_HEAD`, `list_add`, `list_add_tail`, `list_empty`, `list_del`, `list_move`, and `list_move_tail`.
- Provides `list_entry`, `list_first_entry`, raw iteration, safe iteration, entry iteration, and safe entry iteration macros.
- Includes poison pointer constants but does not assign them on delete.

Role: lets OCF list-using code build without depending on Linux kernel list headers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/env_ocf/ocf_env_list.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/event/Makefile -->
# File Research: sources/virtualization/spdk/lib/event/Makefile

Builds the SPDK event library.

Important behavior:
- Declares shared object version `16.0`.
- Adds environment CFLAGS and suppresses packed-member address warnings.
- Builds `app.c`, `reactor.c`, `log_rpc.c`, `app_rpc.c`, and `scheduler_static.c`.
- Uses `spdk_event.map` as the library version/map file.
- Includes the common SPDK library make rules.

Role: groups the application framework, reactor runtime, logging RPCs, framework RPCs, and static scheduler into `libspdk_event`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/event/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/event/app.c -->
# File Research: sources/virtualization/spdk/lib/event/app.c

Implements SPDK's application framework lifecycle, option parsing, environment setup, trace setup, RPC bootstrap, signal handling, and shutdown.

Important behavior:
- Defines default app/DPDK/log/trace options and initializes `struct spdk_app_opts` with ABI-size-aware field assignment.
- Parses global SPDK CLI options including config JSON, CPU mask/lcores, hugepage/memory options, PCI allow/block, RPC socket, trace settings, interrupt mode, and NUMA enforcement.
- Initializes the env layer via `spdk_env_init()`, starts reactors, creates the app thread, sets up trace shared memory, and loads JSON startup/runtime configuration.
- Starts or skips the RPC server depending on options, with support for delayed subsystem init via `--wait-for-rpc`.
- Uses `/var/tmp/spdk_cpu_lock_%03d` lock files to prevent multiple SPDK processes from claiming the same cores unless disabled.
- Installs signal handlers for SIGINT/SIGTERM shutdown and ignores SIGPIPE.
- Tracks baseline per-core `/proc/stat` or FreeBSD CPU time counters for later reactor stats.
- Handles `spdk_app_stop()`, subsystem fini, RPC finish, reactor stop, trace cleanup, env cleanup, and log close.

Registered framework RPCs in this file:
- `framework_start_init`
- `framework_wait_init`
- `framework_disable_cpumask_locks`
- `framework_enable_cpumask_locks`

Filesystem/storage relevance: this is the entrypoint lifecycle used by SPDK storage applications before block, NVMe, vhost, or filesystem-device services are initialized.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/event/app.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/event/app_rpc.c -->
# File Research: sources/virtualization/spdk/lib/event/app_rpc.c

Implements JSON-RPC methods for SPDK application/framework introspection and runtime control.

Important RPCs:
- `spdk_kill_instance`: sends a decoded signal to the current process.
- `framework_monitor_context_switch`: gets/sets context-switch monitoring.
- `thread_get_stats`: returns per-SPDK-thread busy/idle ticks, cpumask, and poller counts.
- `thread_get_pollers`: lists active, timed, and paused pollers per thread.
- `thread_get_io_channels`: lists IO channels per thread.
- `framework_get_reactors`: returns per-reactor lcore, NUMA, TID, busy/idle, interrupt state, OS CPU stats, optional governor frequency, and lightweight threads.
- `framework_set_scheduler` / `framework_get_scheduler`: controls and reports scheduler name, period, isolated core mask, scheduling core, governor, and scheduler-specific options.
- `framework_get_governor`: reports governor-specific data and per-core frequency data.
- `scheduler_set_options`: startup-only scheduler core and isolated-core-mask configuration.
- `thread_set_cpumask`: updates a thread cpumask asynchronously on the target SPDK thread.

Integration details:
- Uses `spdk_for_each_thread()` and `spdk_for_each_reactor()` to gather distributed runtime state.
- Uses generated RPC decoder/free helpers from `spdk_internal/rpc_autogen.h`.
- Validates cpumasks against the active reactor mask and interrupt-mode scheduling constraints.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/event/app_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/event/event_internal.h -->
# File Research: sources/virtualization/spdk/lib/event/event_internal.h

Internal header shared by event framework sources.

Important contents:
- Defines `struct spdk_lw_thread`, the reactor-side context attached to each SPDK thread.
- Tracks current and initial lcore, reschedule flag, scheduling timestamp, lifetime stats, and current scheduling-period stats.
- Declares `app_get_proc_stat()` for OS CPU usage deltas.
- Declares scheduler isolated-core-mask getters/setters.

Role: connects `reactor.c`, `app.c`, scheduler code, and framework RPC reporting without exposing these details as public API.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/event/event_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/event/log_rpc.c -->
# File Research: sources/virtualization/spdk/lib/event/log_rpc.c

Implements JSON-RPC methods for SPDK logging control.

Important RPCs:
- `log_set_print_level` and `log_get_print_level`
- `log_set_level` and `log_get_level`
- `log_set_flag`, `log_clear_flag`, and `log_get_flags`
- `log_enable_timestamps`

Important behavior:
- Converts internal log levels to strings: `ERROR`, `WARNING`, `NOTICE`, `INFO`, `DEBUG`.
- Uses generated decoder/free helpers for log-level and string parameters.
- Exposes startup/runtime control for most log settings; timestamp enablement is runtime-only.
- Registers the `log_rpc` log component.

Role: provides dynamic observability controls for SPDK applications without restart.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/event/log_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/event/reactor.c -->
# File Research: sources/virtualization/spdk/lib/event/reactor.c

Implements SPDK's reactor runtime: event queues, per-core reactor loops, SPDK thread scheduling, interrupt-mode support, scheduler/governor registration, and scheduler tracepoints.

Important behavior:
- Initializes one `struct spdk_reactor` per active env lcore with an event ring, optional eventfds/fd-group interrupt support, and a thread queue.
- Creates the global event mempool and initializes the SPDK thread library with reactor-specific thread operations.
- `spdk_event_allocate()` and `spdk_event_call()` enqueue cross-core events and notify interrupt-mode reactors when needed.
- Reactor loops run event batches, poll SPDK threads, update busy/idle TSC accounting, monitor context switches, and initiate periodic scheduler passes.
- Thread scheduling chooses a target lcore from the thread cpumask, round-robins via `g_next_core`, and respects interrupt-mode limitations.
- Supports thread reschedule requests and scheduler-driven migrations using `struct spdk_lw_thread`.
- `spdk_for_each_reactor()` serializes callbacks across all reactors and completes on the original reactor.
- Linux interrupt mode uses `eventfd` plus `spdk_fd_group` for event queue and reschedule notifications.
- Scheduler infrastructure registers, selects, initializes/deinitializes, runs balance phases, tracks isolated cores, and updates per-core interrupt modes.
- Governor infrastructure registers and selects CPU governors.
- Registers scheduler tracepoint descriptions for scheduler period start, core stats, thread stats, and thread moves.

Lifecycle notes:
- `spdk_reactors_start()` launches remote lcore reactor threads and runs the current-core reactor inline until stop.
- `spdk_reactors_stop()` schedules a final reactor iteration that sets state to exiting and wakes reactors.
- `spdk_reactors_fini()` requires all reactor thread queues to be empty before freeing rings, fd groups, mempool, and arrays.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/event/reactor.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/event/scheduler_static.c -->
# File Research: sources/virtualization/spdk/lib/event/scheduler_static.c

Implements SPDK's static scheduler.

Important behavior:
- First initialization disables periodic scheduling by setting scheduler period to zero.
- On later reloads, sets a short period to restore threads to their saved initial lcores.
- `balance_static()` sets all cores to polling mode, restores each thread's target lcore from `lw_thread->initial_lcore`, then disables further balancing.
- Supports startup JSON options with a `mappings` string that maps thread IDs to core IDs.
- Validates thread existence, core existence, and thread cpumask compatibility before applying mappings.
- Registers as scheduler name `static`.

Role: provides deterministic thread placement and a baseline scheduler that performs no ongoing load balancing.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/event/scheduler_static.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/fsdev/Makefile -->
# File Research: sources/virtualization/spdk/lib/fsdev/Makefile

Builds the SPDK filesystem-device library.

Important behavior:
- Declares shared object version `4.0`.
- Builds `fsdev.c`, `fsdev_io.c`, and `fsdev_rpc.c`.
- Sets `LIBNAME = fsdev`.
- Uses `spdk_fsdev.map` as the symbol map.
- Includes common SPDK library make rules.

Role: build metadata for SPDK's fsdev abstraction, which is adjacent to virtualization/filesystem integration but whose implementation files are outside this grouped item.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/fsdev/Makefile -->