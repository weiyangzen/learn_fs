# Research group subset-b-003705

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_perfcnt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_perfcnt.c

### Purpose
`panfrost_perfcnt.c` implements Panfrost's unstable performance-counter uAPI. It owns the device-wide counter session, allocates a GPU-visible sample buffer in the calling file's MMU context, programs JM/shader/tiler/MMU-L2 counter enable registers, triggers manual samples, and copies the raw counter dump back to userspace.

### Important APIs, types, and functions
The central private type is `struct panfrost_perfcnt`, which stores the active GEM mapping, buffer size, CPU vmap, owning `panfrost_file_priv`, mutex, and completion. External entry points are `panfrost_perfcnt_init()`, `panfrost_perfcnt_fini()`, `panfrost_perfcnt_close()`, `panfrost_ioctl_perfcnt_enable()`, `panfrost_ioctl_perfcnt_dump()`, `panfrost_perfcnt_sample_done()`, and `panfrost_perfcnt_clean_cache_done()`. Internal helpers are `panfrost_perfcnt_enable_locked()`, `panfrost_perfcnt_disable_locked()`, and `panfrost_perfcnt_dump_locked()`.

### Control flow
Initialization computes the raw dump size from GPU feature registers: v4 GPUs use coregroup count, older layouts use L2 count and highest shader index plus JM and tiler blocks. Enable first passes `panfrost_unstable_ioctl_check()`, rejects invalid Bifrost counter-set selection, takes the perfcnt mutex, runtime-resumes the GPU, creates a shmem BO, opens it on the file, gets the file's GPU mapping, vmaps it, clears counters and caches, obtains an MMU address space, enables all counter blocks, applies the 8186 tiler workaround, and switches `GPU_PERFCNT_CFG` to manual mode. Dump programs the sample base address, clears relevant IRQ bits, issues `GPU_CMD_PERFCNT_SAMPLE`, waits for the cache-clean completion, then copies `bosize` bytes to the user pointer. Close disables counters automatically if the closing file owns the session.

### State and persistence behavior
Only one file can own perfcnt collection at a time through `perfcnt->user`; competing enables return `-EBUSY`. The active BO and address-space slot persist until disable or file close. The completion is signaled indirectly by GPU interrupt handling: sample completion issues a cache clean, and clean completion wakes dump waiters. Disable tears down hardware enables, vmap, GEM file open, AS reference, mapping reference, and runtime-PM reference.

### Dependencies and integration points
The file depends on Panfrost GEM/MMU/job/device helpers, register macros from `panfrost_regs.h`, GPU feature helpers, DRM shmem GEM, runtime PM, completions, and uAPI structs from `panfrost_drm.h`. It integrates with Panfrost ioctl dispatch, file close handling, and GPU IRQ paths that call the `*_done()` callbacks.

### Risks
High-risk areas are exclusive ownership, timeout/error unwind, and raw counter exposure. The unstable uAPI gate is important because the raw dump layout is hardware-specific. Incorrect BO lifetime or missing `panfrost_mmu_as_put()` can leak mappings or AS slots. Interrupt ordering matters because the sample is not considered ready until caches are cleaned. The 8186 workaround must keep tiler counters disabled only across the sensitive enable window.

### Test signals
Useful tests include enable/dump/disable on Midgard and Bifrost, invalid counter-set rejection, concurrent file ownership returning `-EBUSY`, owner-only dump and disable, file-close cleanup, runtime suspend after disable, sample timeout injection, and validation that dump sizes match GPU feature-derived layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_perfcnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_perfcnt.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_perfcnt.h

### Purpose
`panfrost_perfcnt.h` is the internal declaration point for Panfrost performance-counter lifecycle, interrupt callbacks, file cleanup, and ioctl handlers.

### Important APIs, types, and functions
It declares `panfrost_perfcnt_sample_done()`, `panfrost_perfcnt_clean_cache_done()`, `panfrost_perfcnt_init()`, `panfrost_perfcnt_fini()`, `panfrost_perfcnt_close()`, `panfrost_ioctl_perfcnt_enable()`, and `panfrost_ioctl_perfcnt_dump()`. It includes `panfrost_device.h` so callers can pass `struct panfrost_device *`; DRM file/device types are provided transitively by the driver headers.

### Control flow
The header has no runtime flow. Device setup calls init/fini, GPU IRQ handling calls the completion callbacks, ioctl tables call the enable and dump handlers, and file close calls `panfrost_perfcnt_close()` to drop ownership.

### State and persistence behavior
The header owns no storage, but it defines the cross-file contract for `pfdev->perfcnt` state allocated in the implementation. The close hook is part of the persistence contract because perfcnt sessions are file-owned and must not survive their DRM file.

### Dependencies and integration points
It links the perfcnt implementation to Panfrost device, job IRQ, DRM ioctl, and file-private code. Any prototype change must remain synchronized with the ioctl table and IRQ callbacks.

### Risks
The main risk is missing a lifecycle hook in a caller: failing to call close or fini leaves hardware counters and mappings active longer than intended. Because the ioctl ABI is unstable and raw, declarations should stay narrow.

### Test signals
Build coverage across Panfrost ioctl, device init/fini, and IRQ code validates the declarations. Runtime tests should verify file close disables a live counter session.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_perfcnt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_regs.h

### Purpose
`panfrost_regs.h` defines the Midgard/Bifrost GPU, job-slot, power, performance-counter, coherency, and MMU register offsets and bit fields used by the Panfrost driver.

### Important APIs, types, and functions
The file is macro-only. Major groups include GPU identification and feature registers, interrupt status/mask bits, `GPU_CMD` commands, performance-counter base/config/enable registers, cycle/timestamp registers, coherency controls, shader/tiler/L2 power state and transition registers, implementation config bits, job-slot register macros under `JS_*`, MMU interrupt and address-space macros under `AS_*`, LPAE/AArch64 translation flags, fault status fields, and `gpu_write()`/`gpu_read()` MMIO helpers.

### Control flow
There is no executable control flow. Driver code selects offsets by block and slot number, writes command values to start reset/cache/perfcnt operations, polls status registers, and decodes fault or feature fields through these macros.

### State and persistence behavior
The macros name persistent hardware state: IRQ masks, power state, active address-space translation tables, job-slot descriptors, perfcnt configuration, coherency protocol, and implementation workarounds. Writes can persist until explicitly cleared or the GPU is reset, so definitions must match the hardware contract exactly.

### Dependencies and integration points
Consumers include Panfrost GPU reset/power code, job submission, MMU setup/fault handling, perfcnt, feature probing, and cache maintenance. The helper macros assume a driver object with `iomem`, which is supplied by Panfrost device state.

### Risks
Incorrect offsets or masks can corrupt unrelated MMIO state, hang job slots, misprogram MMU translations, or expose invalid counter data. Slot/address-space stride macros are especially sensitive because they generate register addresses from user-visible job or VM choices. Several config bit names are generation-specific, so new GPUs must be checked before reuse.

### Test signals
Build all Panfrost objects, boot on representative Midgard and Bifrost GPUs, exercise MMU faults, job completion, reset, power cycling, cache flushes, perfcnt sampling, and compare register dumps against vendor documentation or known-good traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/Kconfig

### Purpose
`panthor/Kconfig` declares the `DRM_PANTHOR` build option for ARM Mali CSF-based Valhall/Immortalis GPUs.

### Important APIs, types, and functions
The single config symbol is `DRM_PANTHOR`, a tristate named "Panthor (DRM support for ARM Mali CSF-based GPUs)". It depends on DRM, ARM or ARM64 or COMPILE_TEST, non-`GENERIC_ATOMIC64`, and MMU. It selects devfreq simple ondemand, DRM exec, GEM shmem, GPUVM, scheduler, LPAE io-pgtable, IOMMU support, and PM devfreq.

### Control flow
Kconfig controls whether `panthor.o` is built into the kernel, built as a module, or omitted. The selected symbols ensure memory management, scheduling, and DVFS helpers are available before the driver compiles.

### State and persistence behavior
The file has no runtime state. Its persistent effect is the kernel configuration dependency graph and the availability of the Panthor platform driver.

### Dependencies and integration points
It integrates with the DRM GPU driver menu and the Makefile's `obj-$(CONFIG_DRM_PANTHOR)` rule. The help text clarifies scope: CSF Valhall Gxxx GPUs use Panthor, while non-CSF Valhall Mali-G68/G78 remain Panfrost territory.

### Risks
Dependency mistakes show up as build failures or unsupported runtime combinations. The `!GENERIC_ATOMIC64` condition is tied to `IOMMU_IO_PGTABLE_LPAE`; loosening it without testing could break page-table atomics. Missing selects can silently disable scheduler, VM, or devfreq features the source assumes.

### Test signals
Check `allmodconfig`, `COMPILE_TEST`, ARM, and ARM64 builds; verify module and built-in configurations; and confirm non-CSF Panfrost targets are not accidentally routed to Panthor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/Makefile

### Purpose
`panthor/Makefile` defines the object list for the composite Panthor DRM driver.

### Important APIs, types, and functions
`panthor-y` links `panthor_devfreq.o`, `panthor_device.o`, `panthor_drv.o`, `panthor_fw.o`, `panthor_gem.o`, `panthor_gpu.o`, `panthor_heap.o`, `panthor_hw.o`, `panthor_mmu.o`, `panthor_pwr.o`, and `panthor_sched.o`. `obj-$(CONFIG_DRM_PANTHOR) += panthor.o` exposes the composite object to Kbuild. `CFLAGS_panthor_gpu.o := -I$(src)` adds the source directory include path for generated trace header use.

### Control flow
There is no runtime flow. Build flow compiles each subsystem object and links it into one module or built-in object when Kconfig enables Panthor.

### State and persistence behavior
The Makefile owns no runtime state. Its persistent build state is the exact set of subsystems included in the driver; omitting one would create link failures or runtime feature gaps.

### Dependencies and integration points
The object list mirrors the driver's subsystem split: platform/ioctl entry, device lifecycle, firmware, GEM, GPU block, tiler heaps, hardware matching, MMU, power controller, scheduler, and devfreq. It integrates with the parent DRM Makefile through the `CONFIG_DRM_PANTHOR` object rule.

### Risks
Object ordering is normally not semantically important for kernel links, but missing files are. The per-object CFLAGS line is easy to drop during refactors, which can break trace include resolution in `panthor_gpu.c`.

### Test signals
Compile `CONFIG_DRM_PANTHOR=m` and `=y`, clean-build after touching trace headers, and ensure every object listed by public headers is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_devfreq.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_devfreq.c

### Purpose
`panthor_devfreq.c` implements Panthor DVFS integration using Linux devfreq, OPP tables, the simple_ondemand governor, optional cooling device registration, and scheduler-provided busy/idle accounting.

### Important APIs, types, and functions
`struct panthor_devfreq` stores the devfreq device, governor thresholds, accumulated busy/idle times, last update time, last busy state, and spinlock. Public functions are `panthor_devfreq_init()`, `panthor_devfreq_resume()`, `panthor_devfreq_suspend()`, `panthor_devfreq_record_busy()`, `panthor_devfreq_record_idle()`, and `panthor_devfreq_get_freq()`. Devfreq profile callbacks are `panthor_devfreq_target()`, `panthor_devfreq_get_dev_status()`, and `panthor_devfreq_get_cur_freq()`.

### Control flow
Initialization allocates managed state, discovers or installs an OPP table, configures the `mali` regulator for OPP and keeps optional `sram` enabled, selects the current recommended OPP, records `ptdev->fast_rate` from the highest OPP, sets simple_ondemand thresholds, adds the devfreq device, and registers a thermal cooling device if possible. Busy/idle notifications update elapsed time under the spinlock. The devfreq poll callback snapshots current clock rate, rolls the current interval into busy or idle time, returns nanosecond totals, and resets accounting.

### State and persistence behavior
Utilization state persists in `ptdev->devfreq` across polling intervals and is reset on resume and every status query. `ptdev->fast_rate` persists for fdinfo reporting. OPP/regulator/devfreq resources are devm/drmm managed for device lifetime. Suspend and resume delegate to devfreq core only when a devfreq device was successfully created.

### Dependencies and integration points
The file depends on `clk`, `devfreq`, `devfreq_cooling`, OPP, regulators, DRM managed allocation, and `panthor_device`. Scheduler or GPU activity paths call record busy/idle; fdinfo queries call `panthor_devfreq_get_freq()`; device PM calls suspend/resume.

### Risks
The status debug print divides by `status->total_time / 100`, so a very small interval can be risky if total time is below 100 ns. OPP/provider assumptions are platform-sensitive: power domains may already own OPP setup, while regulator coupling needs the SRAM supply kept enabled. Missing busy/idle transitions produce misleading DVFS decisions.

### Test signals
Use platforms with DT OPP tables and power-domain-provided OPPs, verify frequency scaling under GPU load and idle, inspect fdinfo max/current frequency, test runtime suspend/resume, cooling registration, regulator deferral, and lockdep around concurrent busy/idle and devfreq polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_devfreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_devfreq.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_devfreq.h

### Purpose
`panthor_devfreq.h` exposes the Panthor frequency-management hooks used by device lifecycle, scheduler activity tracking, and fdinfo.

### Important APIs, types, and functions
It forward-declares `struct panthor_device` and `struct panthor_devfreq`, plus devfreq/cooling types, and declares `panthor_devfreq_init()`, `panthor_devfreq_resume()`, `panthor_devfreq_suspend()`, `panthor_devfreq_record_busy()`, `panthor_devfreq_record_idle()`, and `panthor_devfreq_get_freq()`.

### Control flow
The header has no executable flow. Device init calls init, PM paths call suspend/resume, scheduler or power state transitions call record busy/idle, and fdinfo calls get frequency.

### State and persistence behavior
No storage is owned here. The declared API manipulates `ptdev->devfreq` and `ptdev->fast_rate` in implementation code.

### Dependencies and integration points
This header is included by `panthor_device.c` and `panthor_drv.c`, and can be included by scheduler code that reports activity. It keeps devfreq internals opaque to most of the driver.

### Risks
The declarations assume callers tolerate a device without devfreq support because implementation functions are mostly no-ops when initialization did not create `pdevfreq->devfreq`.

### Test signals
Build coverage of device, driver, and scheduler objects validates includes. Runtime tests should confirm busy/idle hooks are paired around submitted work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_devfreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_device.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_device.c

### Purpose
`panthor_device.c` owns Panthor device bring-up, teardown, reset work, runtime PM transitions, coherency selection, MMIO mmap fault handling, and exception-name decoding.

### Important APIs, types, and functions
External functions are `panthor_device_init()`, `panthor_device_unplug()`, `panthor_device_mmap_io()`, `panthor_device_resume()`, `panthor_device_suspend()`, and `panthor_exception_name()`. Important helpers include `panthor_gpu_coherency_init()`, `panthor_clk_init()`, `panthor_init_power()`, `panthor_device_reset_work()`, `panthor_device_resume_hw_components()`, and the MMIO fault operations.

### Control flow
Init records SoC data, initializes locks/completions/debugfs lists, allocates a dummy latest-flush page, creates the ordered reset workqueue, gets clocks and power domains, initializes devfreq, maps MMIO, enables runtime PM, resumes the device, probes hardware, initializes power/GPU/coherency/MMU/firmware/scheduler/GEM, enables autosuspend, and registers the DRM device. Unwind unplug order is scheduler, firmware, MMU, GPU, power, then PM put. Reset work skips if not active, enters the DRM device, performs scheduler/FW/MMU pre-reset, soft resets, powers L2, restores MMU/FW, clears pending, and reports scheduler recovery or unplugs on fatal FW reboot failure.

### State and persistence behavior
`struct panthor_device` state is initialized here: PM state atomics, reset pending/fast flags, unplug completion, dummy flush page, clocks, MMIO base, physical address, runtime-PM autosuspend, and subsystem pointers. Suspend replaces user MMIO mappings with dummy page mappings before power-off; resume unmaps dummy mappings and returns to real noncached MMIO after hardware components are restored.

### Dependencies and integration points
The file integrates all major Panthor subsystems: devfreq, power, GPU, hardware probing, MMU, firmware, scheduler, GEM, DRM registration, runtime PM, platform resources, and user mmap support from `panthor_drv.c`.

### Risks
Initialization and unwind ordering are high risk because later blocks depend on earlier power/MMU/FW state. User MMIO mapping is race-sensitive and relies on `pm.mmio_lock` plus state transitions to prevent external aborts while suspended. Reset must coordinate scheduler, firmware, MMU, and power without running during suspend. Unplug can race reset and remove, so the unplug lock/completion contract is critical.

### Test signals
Probe/remove, module unload, runtime suspend/resume with user MMIO mappings, forced reset, FW boot failure, coherency-capable and noncoherent systems, power-domain attachment, and lockdep around reset versus suspend are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_device.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_device.h

### Purpose
`panthor_device.h` defines the core Panthor device and file-private state, common IRQ helper machinery, PM/reset state enums, exception codes, MMIO accessors, and lifecycle prototypes.

### Important APIs, types, and functions
Key types include `struct panthor_soc_data`, `enum panthor_device_pm_state`, `enum panthor_irq_state`, `struct panthor_irq`, profiling flags, `struct panthor_device`, `struct panthor_gpu_usage`, and `struct panthor_file`. It declares device init/unplug/mmap/PM and exception-name functions. Inline helpers include `panthor_device_schedule_reset()`, `panthor_device_reset_is_pending()`, `panthor_device_resume_and_get()`, `panthor_exception_is_fault()`, 32/64-bit MMIO read/write helpers, stable 64-bit counter reads, and poll macros. `PANTHOR_IRQ_HANDLER()` generates raw/threaded IRQ handlers plus suspend/resume and mask update helpers for each interrupt block.

### Control flow
The IRQ macro is the main encoded flow: raw handler checks status, atomically moves ACTIVE to PROCESSING, masks interrupts, wakes the threaded handler, the thread drains raw status through a subsystem callback, then restores the saved mask if still active. Suspend/resume helpers synchronize IRQ state and hardware masks.

### State and persistence behavior
`struct panthor_device` embeds persistent DRM device state, SoC data, MMIO mapping, clocks, coherency and GPU/CSIF info, subsystem pointers, unplug synchronization, reset work, PM mapping state, profiling flags, max clock, and debugfs GEM list. `struct panthor_file` owns per-open VM and group pools, user MMIO offset selection, and accounting stats.

### Dependencies and integration points
Almost every Panthor subsystem includes this header. It bridges DRM core, GPU scheduler, io-pgtable, runtime PM, regulator, Panthor uAPI, and low-level register access.

### Risks
This header has broad blast radius. The IRQ macro's state/mask ordering prevents shared-IRQ races; changing it can lose interrupts or process while suspended. `panthor_file.user_mmio.offset` is explicitly untrusted after mmap adjustment, and bypassing that rule can branch on user-controlled offsets. PM recovery in `panthor_device_resume_and_get()` depends on `recovery_needed` atomics.

### Test signals
Build all Panthor objects, run IRQ storm and suspend/resume tests, test 32-bit userspace MMIO offset selection on arm64, reset scheduling from multiple subsystems, and exception decoding in scheduler fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_drv.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_drv.c

### Purpose
`panthor_drv.c` is the Panthor DRM front door. It implements uAPI object copying, DRM ioctls, syncobj/timeline dependency handling, VM and group operations, BO creation/query/sync/labeling, tiler heap ioctls, mmap dispatch, fdinfo/debugfs, platform probe/remove, sysfs profiling, module init, and driver registration.

### Important APIs, types, and functions
Important local types are `struct panthor_sync_signal`, `struct panthor_job_ctx`, and `struct panthor_submit_ctx`. Core helpers are `panthor_set_uobj()`, `panthor_get_uobj_array()`, `panthor_check_sync_op()`, the submit-context collect/dependency/arm/push helpers, `panthor_query_timestamp_info()`, and `group_priority_permit()`. Ioctl handlers cover `DEV_QUERY`, `VM_CREATE/DESTROY/BIND/GET_STATE`, `BO_CREATE/MMAP_OFFSET/SET_LABEL/SYNC/QUERY_INFO`, `GROUP_CREATE/DESTROY/SUBMIT/GET_STATE`, `TILER_HEAP_CREATE/DESTROY`, and `SET_USER_MMIO_OFFSET`. Driver hooks include `panthor_open()`, `panthor_postclose()`, `panthor_mmap()`, `panthor_probe()`, and `panthor_remove()`.

### Control flow
Open allocates a `panthor_file`, chooses a user MMIO offset, and creates VM and group pools. Query ioctls either return object sizes or copy versioned structs back to userspace. Group submit and async VM bind copy user arrays, create scheduler jobs, collect signal ops first, prepare reservation objects with `drm_exec`, add wait dependencies including intra-batch signal dependencies, arm jobs, update signal fences, push jobs, then publish fences to syncobjs. Mmap checks whether the offset falls in the per-file MMIO aperture and dispatches either to `panthor_device_mmap_io()` or GEM mmap.

### State and persistence behavior
Per-file state persists in VM/group pools and accumulated fdinfo stats. Submit context state is temporary and cleaned on every path; jobs become scheduler-owned only after the no-fail push point. The module owns `panthor_cleanup_wq`, the platform driver, a transparent hugepage module parameter, and a sysfs `profiling` mask that toggles fdinfo sampling.

### Dependencies and integration points
The file connects DRM core ioctls, syncobj/timeline fences, GPU scheduler, DRM exec, Panthor MMU/scheduler/GEM/heap/devfreq/FW/device helpers, platform OF matching, runtime PM, arch timer timestamping, debugfs, and uAPI definitions in `panthor_drm.h`.

### Risks
uAPI validation is security-critical: object sizes, strides, padding, flags, priorities, sync handles, and offsets all need strict checks. Submit batching is lifetime-sensitive because fences may reference earlier jobs in the same batch. Nothing may fail after jobs are pushed and syncobjs updated. Timestamp queries temporarily disable preemption/IRQs for closeness and must remain bounded. MMIO offset handling must use the READ_ONCE local copy to avoid user-controlled races.

### Test signals
Run IGT or Mesa Panthor uAPI coverage: versioned queries, 32-bit compat mmap, VM bind sync/async, multi-job submit with timeline syncobjs, intra-batch waits, invalid flags/padding, priority permission checks, BO cache sync, fdinfo profiling, probe/remove, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_drv.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_drv.h

### Purpose
`panthor_drv.h` currently exposes the transparent hugepage module parameter to other Panthor source files.

### Important APIs, types, and functions
It declares `extern bool panthor_transparent_hugepage;`, defined in `panthor_drv.c` when transparent hugepage support is enabled. There are no functions or types.

### Control flow
No runtime flow lives here. `panthor_gem.c` reads the variable during GEM initialization to decide whether to create/use a hugepage mount.

### State and persistence behavior
The variable is module-global state configured through the `transparent_hugepage` module parameter. It affects GEM initialization policy for the device lifetime.

### Dependencies and integration points
This header is included by `panthor_gem.c`; the backing symbol and module parameter are in `panthor_drv.c`.

### Risks
The header is intentionally small. The main risk is configuration mismatch when `CONFIG_TRANSPARENT_HUGEPAGE` is off; consumers must only rely on the symbol in compatible builds as the current implementation does.

### Test signals
Compile with and without transparent hugepage support, boot with `panthor.transparent_hugepage=0`, and verify GEM init logs do or do not report hugepage usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_fw.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_fw.c

### Purpose
`panthor_fw.c` manages Mali CSF firmware: loading and validating the firmware binary, mapping firmware sections into the MCU VM, deriving host/FW shared interfaces, starting/stopping/halting the MCU, handling job/global interrupts, request-ack waiting, doorbells, watchdog pings, and reset/unplug firmware recovery.

### Important APIs, types, and functions
Private types describe firmware headers, section entries, iterators, sections, interface arrays, and `struct panthor_fw`. Public entry points include `panthor_fw_init()`, `panthor_fw_unplug()`, `panthor_fw_pre_reset()`, `panthor_fw_post_reset()`, `panthor_fw_vm()`, `panthor_fw_get_glb_iface()`, `panthor_fw_get_csg_iface()`, `panthor_fw_get_cs_iface()`, endpoint request get/set/update helpers, `panthor_fw_glb_wait_acks()`, `panthor_fw_csg_wait_acks()`, `panthor_fw_ring_csg_doorbells()`, `panthor_fw_alloc_queue_iface_mem()`, and `panthor_fw_alloc_suspend_buf_mem()`.

### Control flow
Init allocates firmware state, requests the job IRQ, powers L2, creates a 4 GB MCU VM with a shared region aperture, loads `arm/mali/arch<major>.<minor>/mali_csffw.bin`, activates the VM, starts the MCU, initializes global/CSG/CS interface pointers from the shared section, programs timers/core masks/ack IRQ masks, enables idle/counters/allocation timers, rings the global doorbell, and schedules watchdog pings. Loading validates the binary magic/version/size, iterates entries, accepts IFACE and build-info entries, ignores known optional metadata, rejects unsupported mandatory entries, checks address/data ranges and page alignment, creates kernel BOs at firmware VAs, copies initial data, maps shared sections, and syncs pages for device access.

### State and persistence behavior
Persistent state includes the MCU VM, firmware section list with saved initialization data for reloads, shared-section CPU mapping, global/group/stream interface pointers, request waitqueue, boot flag, job IRQ state, and watchdog delayed work. Fast reset is possible only after a clean halt; slow reset reloads all sections. Ack waiting first busy-polls briefly, then sleeps on the FW waitqueue, returning partial ack masks on timeout.

### Dependencies and integration points
The file depends on firmware loader, DMA sync, arch timer or GPU clock timeouts, Panthor GEM/MMU/GPU/HW/scheduler/device helpers, register definitions, IRQ macro generation, and scheduler FW event reporting. Firmware interface structs in `panthor_fw.h` are consumed heavily by scheduler code.

### Risks
Firmware parsing is security- and robustness-sensitive because malformed firmware controls VAs, sizes, flags, and interface pointers. Shared uncached/write-combined mappings require spinlock-protected req updates instead of atomic cmpxchg. Reset ordering must avoid watchdog pings and IRQ handlers touching stopped hardware. Interface version differences such as 32-bit versus 64-bit endpoint requests must be preserved.

### Test signals
Test valid and corrupted firmware images, missing firmware, all advertised arch firmware paths, MCU boot timeout, watchdog timeout reset, suspend/resume fast reset, forced slow reset with section reload, CSG/global ack timeout paths, scheduler event delivery from job IRQ, and interface version compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_fw.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_fw.h

### Purpose
`panthor_fw.h` defines the shared-memory ABI between the Panthor host driver and CSF firmware plus the firmware management API used by scheduler, MMU, GEM, and device PM code.

### Important APIs, types, and functions
The header defines maximum CSG/CS counts, queue ringbuffer interfaces, CS control/input/output interfaces, CSG control/input/output interfaces, global control/input/output interfaces, request/event/state bit masks, endpoint request encoding, timer encoding, perfcnt fields, halt statuses, and wrapper structs `panthor_fw_cs_iface`, `panthor_fw_csg_iface`, and `panthor_fw_global_iface`. It also defines `panthor_fw_toggle_reqs()`, `panthor_fw_update_reqs()`, and `panthor_fw_update_reqs64()` macros and declares all FW management functions.

### Control flow
The core encoded protocol is req/ack toggling: host writes an input `req` bit pattern different from firmware's output `ack`, rings a doorbell, then waits until ack matches req. Update macros preserve unrelated event bits while changing configuration fields under a spinlock. Inline suspend/resume map to pre/post reset.

### State and persistence behavior
The structs map directly onto firmware-owned and host-owned shared memory. Input regions are writable by host; output and control regions are read by host. Lock fields in wrapper structs protect host writes to uncached/WC shared memory. The bit definitions persist as the driver/firmware ABI and are version-sensitive.

### Dependencies and integration points
Scheduler code uses CSG/CS interfaces to start, suspend, resume, doorbell, and inspect command streams. Firmware code initializes pointers and waits for acks. GEM/MMU helpers allocate queue and suspend buffers in the firmware VM.

### Risks
Any layout drift breaks firmware communication. Bit masks must distinguish request bits, event bits, state fields, and config fields; mixing them can lose events or wait forever. The comments about avoiding cmpxchg on uncached mappings are part of the concurrency contract.

### Test signals
Compile-time struct layout awareness, boot with multiple firmware interface versions, exercise CSG start/suspend/resume, endpoint allocation, tiler OOM/resource events, global idle/sleep/ping, and ack timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gem.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gem.c

### Purpose
`panthor_gem.c` implements Panthor GEM object allocation, kernel-only BO mapping into VMs, PRIME import/export cache maintenance, CPU cache sync ioctl support, BO labels, transparent hugepage setup, and debugfs GEM accounting.

### Important APIs, types, and functions
Public functions include `panthor_gem_init()`, `panthor_gem_create_object()`, `panthor_gem_create_with_handle()`, `panthor_kernel_bo_create()`, `panthor_kernel_bo_destroy()`, `panthor_gem_prime_import()`, `panthor_gem_bo_set_label()`, `panthor_gem_kernel_bo_set_label()`, `panthor_gem_sync()`, and debugfs printing. Important internals are `should_map_wc()`, `panthor_gem_free_object()`, PRIME dma-buf ops, `panthor_gem_status()`, and `panthor_gem_funcs`.

### Control flow
GEM init optionally creates a DRM hugepage mount. User BO creation allocates shmem, stores flags, selects WC versus WB mapping, optionally ties the BO reservation object to an exclusive VM root GEM, flushes zeroed pages for WC mappings, creates a GEM handle, and drops the allocation reference. Kernel BO creation allocates shmem, labels/debugfs-tags it, allocates GPU VA, maps it into the selected VM, and returns a wrapper; destroy unmaps, frees VA, drops object and VM references. PRIME export rejects exclusive-VM BOs and installs custom CPU access sync ops. BO sync validates range/type/import status and performs DMA cache maintenance over the requested sg ranges.

### State and persistence behavior
`struct panthor_gem_object` persists flags, optional exclusive VM root GEM, label under mutex, and debugfs metadata. Kernel BO wrappers persist VM pointer, GEM object, VA node, and optional CPU vmap. Imported/exported and resident status is derived from GEM/shmem state. Debugfs maintains a device-wide list of BOs while they are alive.

### Dependencies and integration points
The file depends on DRM GEM shmem, dma-buf, DMA API, Panthor VM mapping, firmware VM for kernel BOs, driver module parameter, and debugfs. `panthor_drv.c` uses it for BO ioctls; firmware, heap, scheduler, and MMU use kernel BO helpers.

### Risks
Cache coherency is the largest risk: coherent devices cannot safely use uncached/WC mappings with shmem zeroing assumptions, while noncoherent mappings need explicit flushes. Exclusive VM BOs must not be exported or rebound elsewhere. Reservation-object substitution to the VM root GEM affects synchronization semantics. Label lifetime uses `kfree_const()` and must remain locked.

### Test signals
Create/map/free user BOs with each flag, import/export PRIME buffers, reject exclusive BO export, run BO_SYNC on partial ranges, verify labels and debugfs totals, exercise transparent hugepage enabled/disabled, and run noncoherent cache-correctness tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gem.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gem.h

### Purpose
`panthor_gem.h` defines Panthor GEM object extensions, kernel BO wrappers, debugfs flag enums, labels, vmap helpers, and GEM/kernel-BO APIs.

### Important APIs, types, and functions
Important types are `struct panthor_gem_debugfs`, `struct panthor_gem_object`, and `struct panthor_kernel_bo`. It defines `PANTHOR_BO_LABEL_MAXLEN`, debugfs state and usage flags, `to_panthor_bo()`, kernel BO GPU VA/size helpers, `panthor_kernel_bo_vmap()`, `panthor_kernel_bo_vunmap()`, and prototypes for GEM allocation, labels, sync, PRIME import, kernel BO create/destroy, and debugfs printing.

### Control flow
Inline vmap maps a kernel BO only once and stores `kmap`; vunmap releases it if present. Other flow is delegated to `panthor_gem.c`.

### State and persistence behavior
The header describes per-BO persistent state: shmem base object, exclusive VM root GEM reference, uAPI create flags, label string protected by a mutex, debugfs creator/usage info, and kernel BO VA/vmap state.

### Dependencies and integration points
It depends on DRM shmem GEM, DRM MM, iosys maps, rwsem types, and Panthor VM forward declarations. Firmware and heap code rely on kernel BO helpers for GPU-visible private memory.

### Risks
The `exclusive_vm_root_gem` contract is central to preventing BO sharing outside a VM. Inline vmap assumes `iosys_map` is CPU-addressable; callers must not use it on failed or destroyed BOs. Label strings may be const or allocated.

### Test signals
Build all users, test kernel BO map/unmap/destroy paths in firmware and heap, verify exclusive VM binding rejection, and inspect debugfs flag reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gpu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gpu.c

### Purpose
`panthor_gpu.c` manages the base GPU interrupt block, DMA mask, coherency/L2 configuration, generic block power on/off helpers, L2 power, cache flush requests, soft reset requests, and GPU block suspend/resume.

### Important APIs, types, and functions
Private state is `struct panthor_gpu`, containing GPU IRQ data, pending request lock, pending request bits, waitqueue, and cache flush mutex. Public functions include `panthor_gpu_init()`, `panthor_gpu_unplug()`, `panthor_gpu_suspend()`, `panthor_gpu_resume()`, `panthor_gpu_power_changed_on/off()`, `panthor_gpu_block_power_on/off()`, `panthor_gpu_l2_power_on/off()`, `panthor_gpu_flush_caches()`, and `panthor_gpu_soft_reset()`. `PANTHOR_IRQ_HANDLER(gpu, ...)` generates IRQ glue.

### Control flow
Init allocates state, configures DMA segment size and coherent mask from GPU PA bits, gets the named GPU IRQ, and requests it with fault/reset/cache-clean masks. IRQ handling clears status, optionally traces power status, logs GPU/protected faults, clears pending request bits, and wakes waiters. Cache flush and reset set a pending bit under lock, write `GPU_CMD`, then wait for the IRQ to clear the bit; timeout schedules reset for cache flush. L2 power-on programs coherency and SoC-specific ASN hash before powering L2.

### State and persistence behavior
`pending_reqs` tracks outstanding reset/cache operations. IRQ mask/state persists in `struct panthor_irq`. `cache_flush_lock` serializes flushes. Coherency mode and L2 config persist in hardware after programming. Unplug suspends IRQ and wakes waiters.

### Dependencies and integration points
The file uses Panthor device and IRQ macros, HW ops, power registers, tracepoints, DMA API, platform IRQs, runtime PM guards, and exception decoding. Hardware dispatch in `panthor_hw.c` points arch v10-v13 ops at these functions.

### Risks
Timeout races are subtle: code rechecks raw IRQ status before declaring timeout. Pending request bits must be protected consistently to avoid lost wakeups. L2 power currently uses only the first core group when multiple L2s are present. DMA mask depends on correctly probed MMU PA bits.

### Test signals
Exercise GPU fault IRQ logging, cache flush success and timeout, soft reset, suspend/resume, L2 power on/off, power trace registration, noncoherent/coherent platforms, and multi-coregroup hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gpu.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gpu.h

### Purpose
`panthor_gpu.h` exposes GPU block lifecycle, power, cache flush, reset, and power-change tracing hooks.

### Important APIs, types, and functions
It declares `panthor_gpu_init()`, `panthor_gpu_unplug()`, `panthor_gpu_suspend()`, `panthor_gpu_resume()`, `panthor_gpu_block_power_on/off()`, `panthor_gpu_l2_power_on/off()`, `panthor_gpu_flush_caches()`, `panthor_gpu_soft_reset()`, and `panthor_gpu_power_changed_on/off()`. Macros `panthor_gpu_power_on()` and `panthor_gpu_power_off()` generate register-specific calls for named GPU blocks.

### Control flow
The header has no direct runtime flow beyond power macros expanding to generic helpers with `<type>_PWRON`, `<type>_PWRTRANS`, `<type>_READY`, and `<type>_PWROFF` register names.

### State and persistence behavior
No state is owned here. The APIs manipulate `ptdev->gpu`, GPU IRQ state, and persistent hardware power/cache/reset registers.

### Dependencies and integration points
It is included by device, firmware, hardware, and power-management code. `panthor_hw.c` binds architecture-specific ops to these functions for pre-arch14 hardware.

### Risks
Power macros rely on register naming consistency in `panthor_regs.h`. Passing a block type without the expected register set will fail at build time or misrepresent readiness behavior.

### Test signals
Compile macro users, power-cycle L2 through HW ops, flush caches during VM updates, and run reset paths on v10-v13 GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_heap.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_heap.c

### Purpose
`panthor_heap.c` manages per-VM tiler heap contexts and chunks for CSF firmware, including user-created heaps, firmware-triggered growth, returning unused chunks, pool lifetime, and memory accounting.

### Important APIs, types, and functions
Private types are `struct panthor_heap_chunk_header`, `struct panthor_heap_chunk`, `struct panthor_heap`, and `struct panthor_heap_pool`. Public APIs include `panthor_heap_create()`, `panthor_heap_destroy()`, `panthor_heap_grow()`, `panthor_heap_return_chunk()`, `panthor_heap_pool_create()`, `panthor_heap_pool_destroy()`, `panthor_heap_pool_get()`, `panthor_heap_pool_put()`, and `panthor_heap_pool_size()`.

### Control flow
Pool creation allocates a kernel BO containing up to 128 GPU heap contexts, vmaps it, and tracks total size. Heap creation validates initial count, max count, and chunk size range/alignment, grabs a VM ref, allocates initial chunks, allocates an xarray ID, zeroes the GPU heap context, and returns heap context and first chunk GPU VAs. Chunk allocation creates a no-mmap kernel BO, maps it no-exec, initializes its header, optionally links it to the previous initial chunk, inserts it into the heap list, and updates pool size. Grow validates the heap VA, checks in-flight and max-chunk limits, allocates a new chunk, and returns encoded VA plus size. Return chunk removes an unlinked chunk by VA.

### State and persistence behavior
A heap pool is refcounted and bound weakly to its VM until destroy sets `pool->vm = NULL`. Heap objects live in an xarray under an rwsem. Each heap tracks chunk list, mutex, sizing limits, target in-flight threshold, and count. `pool->size` accounts context BO plus chunks for fdinfo memory reporting.

### Dependencies and integration points
The file depends on Panthor kernel BO/GEM helpers, VM mapping, register cache-line size, xarray, krefs, and DRM uAPI heap ioctls in `panthor_drv.c`. Firmware/scheduler OOM handling calls grow and return.

### Risks
Heap IDs are inferred from GPU VA offsets, so stride and bounds checks are important. Destroy can race references, hence rwsem plus refcount. Growth currently uses blocking allocation even though firmware OOM handling would prefer nonblocking behavior. Incorrect chunk header linking can confuse firmware tiler allocation.

### Test signals
Create/destroy heaps with boundary chunk sizes and counts, grow until target/max limits, return unused chunks, destroy pool while references exist, verify fdinfo heap memory accounting, and trigger firmware tiler OOM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_heap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_heap.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_heap.h

### Purpose
`panthor_heap.h` declares the tiler heap pool and heap context API used by VM, ioctl, scheduler, and firmware event paths.

### Important APIs, types, and functions
It forward-declares `struct panthor_device`, `struct panthor_heap_pool`, and `struct panthor_vm`, and declares heap create/destroy, pool create/destroy/get/put/size, heap grow, and return chunk functions.

### Control flow
No runtime flow is implemented here. Ioctl paths call create/destroy; VM teardown calls pool destroy; scheduler/FW resource paths call grow/return chunk.

### State and persistence behavior
The opaque pool pointer hides xarray, refcount, VM binding, GPU context BO, and size accounting from callers. Handles returned by create are pool-local.

### Dependencies and integration points
The header is included by `panthor_drv.c`, VM code, and scheduler/resource management code. It isolates heap internals from the uAPI handlers.

### Risks
Callers must hold or acquire pool references where needed because pool destruction invalidates VM association. Heap handles encode with VM IDs in ioctl code, so callers must split them consistently.

### Test signals
Build all heap users, create heaps through ioctl, grow via firmware resource request, and verify pool size is included in memory stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_heap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_hw.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_hw.c

### Purpose
`panthor_hw.c` binds probed Mali GPU architecture versions to Panthor hardware operations, reads GPU identity/features, maps model names, applies optional NVMEM shader masks, and manages power-status trace IRQ registration.

### Important APIs, types, and functions
Private data includes `struct panthor_hw_entry`, `panthor_hw_arch_v10`, `panthor_hw_arch_v14`, and the `panthor_hw_match[]` table. Public functions are `panthor_hw_init()`, `panthor_hw_power_status_register()`, and `panthor_hw_power_status_unregister()`. Helpers include `panthor_hw_gpu_id_init()`, `panthor_hw_bind_device()`, `panthor_gpu_info_init()`, `panthor_hw_info_init()`, `get_gpu_model_name()`, `overload_shader_present()`, and `panthor_hw_set_power_tracing()`.

### Control flow
Hardware init reads `GPU_ID`, binds arch 10-13 to GPU-register reset/L2/power-change ops and arch 14 to PWR-block ops, then reads feature registers and present masks. For arch14+, present masks come from PWR registers; older hardware uses GPU registers. It optionally overrides `shader_present` from an NVMEM cell. Power trace registration finds the platform driver and iterates bound devices to enable or disable power-change IRQ listening.

### State and persistence behavior
`ptdev->hw` points at a static ops table for the device lifetime. `ptdev->gpu_info` is populated with identity, feature, present-mask, coherency, MMU, texture, and thread data that is later exposed through uAPI queries and used by other subsystems. The NVMEM override persists in `gpu_info.shader_present`.

### Dependencies and integration points
The file depends on Panthor GPU/PWR ops, register definitions, platform bus driver lookup, DRM logging, and NVMEM. Device init calls `panthor_hw_init()` before GPU/MMU/FW setup; trace code calls the power status register helpers.

### Risks
Unsupported arch matching returns `-EOPNOTSUPP`, so new GPUs need table updates. Model names are heuristic for some product IDs based on shader count and ray-intersection features. NVMEM shader-present overrides can disable cores globally. Power trace registration relies on driver lookup and may only warn if disabling fails partway.

### Test signals
Probe arch10-14 devices, validate uAPI GPU info against registers, test NVMEM shader-present override, verify model-name logging, enable/disable power tracepoints, and confirm arch14 routes reset/L2 through PWR ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_hw.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_hw.h

### Purpose
`panthor_hw.h` defines the architecture-specific hardware operation table and wrappers for reset/L2 power/power-status capabilities.

### Important APIs, types, and functions
It defines `struct panthor_hw_ops` with `soft_reset`, `l2_power_off`, `l2_power_on`, `power_changed_on`, and `power_changed_off`, plus `struct panthor_hw` containing ops. It declares `panthor_hw_init()`, `panthor_hw_power_status_register()`, and `panthor_hw_power_status_unregister()`. Inline wrappers call the selected ops and `panthor_hw_has_pwr_ctrl()` returns true for GPU architecture major 14 or newer.

### Control flow
Callers use the wrapper functions without branching on GPU architecture. `panthor_hw_init()` installs the correct ops table first; later reset, suspend/resume, and tracing code dispatch through `ptdev->hw->ops`.

### State and persistence behavior
The header owns no state, but it defines the shape of `ptdev->hw` persistent dispatch. `panthor_hw_has_pwr_ctrl()` derives behavior from `ptdev->gpu_info.gpu_id`.

### Dependencies and integration points
It includes `panthor_device.h` and `panthor_regs.h`, and is consumed by device, GPU, firmware, and hardware probing code.

### Risks
Wrappers assume `ptdev->hw` and required function pointers are initialized. Optional power-change ops must be checked before direct use, as implementation code does.

### Test signals
Build all wrapper users, boot arch10-13 and arch14 hardware, test reset/L2 power dispatch, and run power-status trace registration on both ops families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_hw.h -->
