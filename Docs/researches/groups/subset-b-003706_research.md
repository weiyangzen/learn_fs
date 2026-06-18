# subset-b-003706 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_mmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_mmu.c

## Purpose
Implements Panthor GPU virtual memory and MMU address-space management. It owns per-file VM pools, `struct panthor_vm`, GPUVA mapping state, io-pgtable page-table operations, AS slot assignment/recycling, MMU fault handling, VM_BIND job scheduling, and debugfs GPUVA inspection.

## Important APIs, Types, and Functions
Key internal types are `panthor_mmu`, `panthor_as_slot`, `panthor_vm_pool`, `panthor_vm`, `panthor_vma`, `panthor_vm_op_ctx`, and `panthor_vm_bind_job`. Exported entry points include `panthor_mmu_init()`, `panthor_mmu_unplug()`, suspend/reset hooks, VM pool helpers, `panthor_vm_create()`, `panthor_vm_map_bo_range()`, `panthor_vm_unmap_range()`, `panthor_vm_bind_job_create()`, reservation helpers, and `panthor_vm_get_bo_for_va()`. Page-table allocation is centralized through `alloc_pt()`/`free_pt()` and the global `pt_cache`.

## Control Flow
Initialization allocates `panthor_mmu`, initializes AS and VM lists, requests the named `mmu` IRQ, creates the VM_BIND workqueue, and clamps VA bits on 32-bit kernels. VM creation validates user/kernel VA split, initializes `drm_mm`, allocates ARM LPAE S1 `io_pgtable_ops`, sets MAIR-derived Mali memory attributes, starts a one-job VM_BIND scheduler, and registers the VM with `drm_gpuvm`. VM activation assigns AS0 to MCU VMs and nonzero AS slots to user VMs, evicting LRU idle VMs when needed, then programs `AS_TRANSTAB`, `AS_MEMATTR`, and `AS_TRANSCFG`. VM idle drops active count and retains the AS on an LRU list until pressure.

Mapping/unmapping first preallocates all VMAs, page-table pages, GEM pins, sg tables, and `drm_gpuvm_bo` objects in `panthor_vm_op_ctx`. Execution then locks the affected MMU region, runs drm_gpuvm state-machine callbacks, updates io-pgtable mappings, flushes/unlocks the region, and cleans deferred objects. Async VM_BIND uses drm_sched; sync paths call the same execution helper directly. MMU IRQ handling decodes page faults, disables the affected AS, marks the VM faulted, and tells the scheduler to terminate/fault relevant work.

## State and Persistence
Persistent runtime state lives in the device-managed `ptdev->mmu`, AS masks, AS slot VM pointers, VM list, VM schedulers, `drm_gpuvm` VA tree, `drm_mm` kernel VA allocator, heap pool pointer, active AS refcount, `destroyed`, `unusable`, `unhandled_fault`, and locked region fields. BO mappings persist as `panthor_vma` objects linked to `drm_gpuvm_bo`. AS bindings persist across idle until recycled, but reset/suspend/unplug clear hardware state and release slots.

## Dependencies and Integration Points
Depends on DRM GPUVM, DRM scheduler, drm_exec/dma_resv, GEM shmem, ARM io-pgtable, platform IRQs, runtime PM, Panthor GEM/heap/GPU/scheduler/device helpers, and register definitions from `panthor_regs.h`. It integrates with scheduler fault paths through `panthor_sched_report_mmu_fault()` and `panthor_sched_prepare_for_vm_destruction()`, with kernel BO/heap code through kernel auto-VA allocation, and with debugfs through `DRM_DEBUGFS_GPUVA_INFO`.

## Risks and Edge Cases
The main risk surface is consistency between drm_gpuvm metadata and io-pgtable state; failures in async VM_BIND intentionally mark VMs unusable. Huge-page partial unmaps require widening locked regions and remapping preserved ranges. AS command timeouts schedule GPU resets. Imported/exclusive BO handling, deferred cleanup outside dma-signaling paths, and LRU AS recycling are concurrency-sensitive. Fault handling is terminal rather than recoverable, so userspace must recreate affected VM/device state.

## Test Signals
Useful signals are VM create/destroy/map/unmap ioctl coverage, overlapping map/remap/unmap cases, huge-page partial unmaps, imported and exclusive BO mapping attempts, AS slot pressure above hardware slots, reset/suspend/resume with active VMs, MMU fault injection, debugfs GPUVA output, dma_resv fence sequencing for VM_BIND, and leak checking of page-table cache/GEM pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_mmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_mmu.h

## Purpose
Declares the public MMU/VM interface used by the Panthor driver. It hides VM internals while exposing lifecycle, mapping, scheduling, reservation, heap, fdinfo, debugfs, and page-table-cache operations.

## Important APIs, Types, and Functions
Forward declarations include `panthor_vm`, `panthor_vma`, `panthor_mmu`, `panthor_gem_object`, and `panthor_heap_pool`. Major exported groups are MMU lifecycle (`panthor_mmu_init()`, reset/suspend/resume/unplug), VM map/query/activity (`panthor_vm_map_bo_range()`, `panthor_vm_unmap_range()`, `panthor_vm_get_bo_for_va()`, `panthor_vm_active()`, `panthor_vm_idle()`), VM pool management, VM_BIND job helpers, dma_resv update helpers, and `panthor_mmu_pt_cache_init()/fini()`.

## Control Flow
Callers initialize the MMU subsystem during device bring-up, create per-file VM pools on file open, create VMs from ioctl paths, use VM_BIND helpers to build scheduler jobs or execute synchronous operations, and tear pools down on file close. Scheduler code activates and idles VMs around group execution, while GEM/kernel BO paths use kernel auto-VA helpers.

## State and Persistence
The header itself stores no state but defines ownership boundaries. `panthor_vm_get()`/`put()` indicate refcounted VM lifetime; VM pools own file handles; VM_BIND jobs own a scheduler job reference; dma_resv helper APIs persist synchronization fences on VM/private and external BO reservations.

## Dependencies and Integration Points
Includes `linux/dma-resv.h` and depends on DRM scheduler, drm_exec, drm_file, Panthor file/device/GEM types, and userspace UAPI structs such as `drm_panthor_vm_create` and `drm_panthor_vm_bind_op`.

## Risks and Edge Cases
The API exposes both sync and async VM_BIND paths, so callers must prepare reservations and reference lifetimes correctly. `PANTHOR_VM_KERNEL_AUTO_VA` is a sentinel magic address and must not be confused with a valid user VA. Activity APIs expose hardware AS state, so scheduler usage must be balanced.

## Test Signals
Header/API compatibility is exercised by compiling all Panthor modules, ioctl tests for VM lifecycle and VM_BIND, scheduler group/job tests that call VM activation, and fdinfo/debugfs builds with relevant config options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_pwr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_pwr.c

## Purpose
Implements support for the newer Panthor PWR_CONTROL block: power IRQ handling, soft reset command completion, L2/shader/tiler power transitions, delegation and retraction of domains between host and MCU, and suspend/resume IRQ masking.

## Important APIs, Types, and Functions
`struct panthor_pwr` stores the IRQ wrapper, pending request mask, waitqueue, and spinlock. Exported functions are `panthor_pwr_init()`, `panthor_pwr_unplug()`, `panthor_pwr_reset_soft()`, `panthor_pwr_l2_power_off()`, `panthor_pwr_l2_power_on()`, `panthor_pwr_suspend()`, and `panthor_pwr_resume()`. Important helpers include `panthor_pwr_reset()`, `panthor_pwr_domain_transition()`, `delegate_domain()`, `retract_domain()`, and `panthor_pwr_domain_force_off()`.

## Control Flow
Initialization exits early when hardware lacks PWR_CONTROL, otherwise allocates `ptdev->pwr`, initializes wait state, obtains the named `gpu` IRQ, and requests a PWR IRQ handler for command/power events. Reset marks `PWR_IRQ_RESET_COMPLETED` pending, clears stale status, writes reset command, and waits on the waitqueue with timeout fallback. L2 power-on verifies allow bits, powers L2 ready cores, then delegates shader and tiler control to MCU. L2 power-off retracts and powers off tiler/shader first, then powers off L2. IRQ handling clears hardware status, reports invalid/disallowed commands, clears matching pending bits, and wakes waiters.

## State and Persistence
Persistent state is `ptdev->pwr`, `pending_reqs`, and the waitqueue. Hardware state is represented by PWR status, ready, transition, and delegation bits. The code does not retain software mirrors of powered cores beyond request completion; it polls registers as the source of truth.

## Dependencies and Integration Points
Depends on Panthor hardware feature detection, GPU register access helpers, the common Panthor IRQ wrapper, platform IRQ lookup, DRM managed allocation, and PWR register macros from `panthor_regs.h`. It coordinates with MCU/firmware ownership by delegating shader and tiler domains after L2 power-up and retracting them before host-forced power-down.

## Risks and Edge Cases
Timeout behavior is critical: reset timeout checks raw IRQ status before failing, while domain transition failures dump power debug registers. L2 cannot be delegated/retracted and shader domains may use RTU subdomain bits when ray traversal exists. Failed delegation after shader success retracts shader. If forced power-off retracts a domain but power-down fails, that domain remains under host control.

## Test Signals
Signals include boot on hardware with and without PWR_CONTROL, soft reset success/timeout, suspend/resume IRQ masking, L2 power cycle, shader/tiler delegation status, forced power-off after simulated hung MCU, invalid command IRQ logging, and register dumps on transition timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_pwr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_pwr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_pwr.h

## Purpose
Declares the Panthor power-control public interface. It is the boundary used by device bring-up, reset, runtime PM, and firmware/power sequencing code.

## Important APIs, Types, and Functions
The header forward-declares `struct panthor_device` and exports `panthor_pwr_init()`, `panthor_pwr_unplug()`, `panthor_pwr_reset_soft()`, `panthor_pwr_l2_power_off()`, `panthor_pwr_l2_power_on()`, `panthor_pwr_suspend()`, and `panthor_pwr_resume()`.

## Control Flow
Device code initializes the block if present, uses soft reset during reset flows, powers L2 on before delegating shader/tiler domains to firmware, powers L2 off after retracting dependent domains, masks IRQs on suspend/unplug, and resumes IRQ handling on resume.

## State and Persistence
The header stores no state. The implementation owns `ptdev->pwr`, pending power requests, and IRQ state. Callers only receive integer success/failure for operations that can block or timeout.

## Dependencies and Integration Points
Integrates with `panthor_device`, runtime reset sequencing, and power management. The API is intentionally narrow so non-PWR_CONTROL hardware can be represented by no-op init/suspend paths in the implementation.

## Risks and Edge Cases
Callers must tolerate `panthor_pwr_init()` returning success without creating `ptdev->pwr` on unsupported hardware. L2 power operations must be ordered relative to MCU/firmware state to avoid powering down delegated domains incorrectly.

## Test Signals
Compile coverage plus reset and runtime PM tests are the key signals. On non-PWR hardware, init/suspend/resume/unplug should be harmless; on PWR hardware, soft reset and L2 on/off should return meaningful errors on disallowed transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_pwr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_regs.h

## Purpose
Defines Panthor GPU, job, MMU, CSF doorbell, and PWR_CONTROL register offsets and bitfield helpers. It is the shared hardware contract for the Panthor driver.

## Important APIs, Types, and Functions
This is macro-only. Major groups cover GPU identity/features/interrupts/commands/status, shader/tiler/L2 present/ready/power registers, coherency and MCU control, job interrupt registers, MMU interrupt and per-AS register windows, `AS_TRANSCFG`/`AS_MEMATTR` encodings, CSF latest flush and doorbells, and PWR interrupt/status/command/domain registers.

## Control Flow
Consumer code uses these constants to build register reads/writes. Examples include MMU AS programming through `AS_TRANSTAB()`, `AS_MEMATTR()`, and `AS_COMMAND()`, scheduler doorbells through `CSF_DOORBELL()`, GPU cache flush command construction with `GPU_FLUSH_CACHES()`, and PWR domain commands with `PWR_COMMAND_DEF()`.

## State and Persistence
The file contains no software state. It defines how persistent hardware state is addressed and decoded, including feature registers, IRQ masks, MMU fault status, power readiness, transition and delegation state, and command encodings.

## Dependencies and Integration Points
Requires Linux bit helpers such as `BIT`, `BIT_U64`, and `GENMASK`. It is included by Panthor GPU, MMU, scheduler, firmware, and power code. Its offsets are based on Arm Mali register maps and must match hardware/firmware expectations.

## Risks and Edge Cases
Incorrect bit shifts or offsets can silently corrupt hardware control. `GPU_COHERENCY_PROT_BIT(name)` relies on token pasting with defined protocol names. AS slot macros assume `MMU_AS_SHIFT` layout. PWR domain IDs double as allowed/delegated bit positions, making command/status coupling important.

## Test Signals
Signals include successful probe feature detection, IRQ handling, MMU AS updates, cache flush completion, CSF job doorbells, PWR domain transitions, and register-level debug traces on real hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_sched.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_sched.c

## Purpose
Implements Panthor CSF scheduling for firmware-managed Mali GPUs. It bridges DRM scheduler jobs to firmware command stream group/queue interfaces, handles group rotation across limited CSG slots, manages queue fences/timeouts/sync waits, responds to firmware events, coordinates resets/suspend, and gathers fdinfo profiling.

## Important APIs, Types, and Functions
Core types are `panthor_scheduler`, `panthor_csg_slot`, `panthor_group`, `panthor_queue`, `panthor_group_pool`, `panthor_job`, syncobj layouts, tick/update contexts, and job ringbuffer instruction builders. Exported APIs include group pool/create/destroy/state functions, `panthor_job_create()`, job ref/VM/reservation helpers, scheduler init/unplug/suspend/resume/reset hooks, MMU fault reporting, firmware event reporting, and fdinfo gatherers.

## Control Flow
Scheduler init reads firmware global/CSG/CS interface capabilities, clamps CSG slots to unique priorities, verifies non-MCU AS availability, initializes queues/lists/workqueues, and publishes CSIF counts. Group creation validates masks/priorities, gets the target VM, allocates suspend/protection buffers, per-queue syncobj BO, queues/ringbuffers/firmware interfaces/profiling slots, inserts the group into idle lists, and marks the xarray handle registered. Job creation validates queue submit arguments, references the group, allocates a done fence for non-empty streams, computes scheduler credits from profiling-enabled instruction count, and initializes a DRM scheduler job.

At run time, `queue_run_job()` resumes the device, initializes the done fence, writes a kernel-generated CS instruction sequence into the queue ringbuffer, advances insert pointers, schedules or doorbells the group, starts timeouts, updates last fence, and records busy state. The tick work snapshots active groups, asks firmware for status updates, picks groups by priority/round-robin while respecting AS-slot limits, suspends/terminates evicted groups, binds and starts/resumes new groups, updates runtime PM/devfreq, and queues the next tick only when needed. Firmware event work processes global idle events, CSG events, CS fatal/fault/tiler-OOM events, sync updates, progress timeouts, and doorbell acknowledgements outside the hard IRQ path.

## State and Persistence
Long-lived state includes scheduler workqueues, tick timing, runnable/idle/waiting lists, CSG slot bindings, runtime PM reference state, reset stopped-groups list, per-group state/fault/timeout/idle/blocked masks, queue ringbuffer and interface BOs, per-queue sync wait state, fence contexts, in-flight job lists, last fences, profiling slots, and fdinfo counters. Hardware-visible state is persisted in firmware input/output interfaces and syncobj BOs mapped into the VM.

## Dependencies and Integration Points
Depends on DRM scheduler/fences/dma_resv, runtime PM, devfreq, Panthor firmware interface helpers, kernel BO/GEM/heap/MMU/GPU/device helpers, CSF register macros, and UAPI group/queue/job structs. Integrates with MMU via `panthor_vm_active()`, `panthor_vm_idle()`, `panthor_vm_get_bo_for_va()`, and MMU fault reports. Tiler OOM integrates with heap growth and queue firmware inputs.

## Risks and Edge Cases
High-risk areas are lock ordering between scheduler lock, reset lock, queue fence locks, and dma-signaling sections; firmware ack timeouts; reset while jobs/groups are active; sync-wait CPU mapping lifetime; tiler OOM allocation outside scheduler lock; empty command streams returning last fence; timeout suspension/resume accounting; and fault attribution from CS extract pointers. CSG priority uniqueness is used to avoid firmware deadlocks, so slot-count clamping is intentional.

## Test Signals
Signals include group create/destroy/state ioctl tests, multiple priorities and more groups than slots to exercise rotation, RT preemption, job submission with/without profiling, empty stream fences, sync wait unblock, tiler OOM growth and ENOMEM fallback, CS fault/fatal IRQ injection, progress timeout, MMU fault propagation, suspend/resume/reset recovery, fdinfo accounting, and lockdep under concurrent submit/destroy/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_sched.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_sched.h

## Purpose
Declares the Panthor scheduler interface used by ioctl, VM/MMU, reset, firmware IRQ, reservation, and fdinfo paths.

## Important APIs, Types, and Functions
Forward declarations cover DRM scheduler, exec, file, memory stats, Panthor device/file/group/job, and UAPI create/submit/state structs. Public functions include group create/destroy/state/pool helpers, job create/ref/put/VM/update helpers, scheduler init/unplug/reset/suspend/resume hooks, MMU fault and VM-destruction notifications, firmware event reporting, and fdinfo memory/profiling gatherers.

## Control Flow
File-open code creates a group pool, ioctl paths create groups and jobs, submit paths prepare reservations and feed jobs to DRM scheduler, firmware IRQ code reports events to the scheduler, reset code brackets the scheduler with pre/post hooks, and VM destruction flushes scheduler eviction work before mappings vanish.

## State and Persistence
The header owns no state but exposes the lifecycle contracts for refcounted jobs and group pools. Group and job objects persist behind opaque handles/references until destroyed and all scheduler/fence references are released.

## Dependencies and Integration Points
Includes no concrete implementation headers beyond declarations, keeping scheduler internals private. It connects UAPI structs, DRM scheduler jobs, VM objects, Panthor file state, firmware events, and fdinfo accounting.

## Risks and Edge Cases
Callers must pair job references, destroy groups before VM teardown where possible, and call reset/suspend hooks in the expected order. `panthor_sched_report_fw_events()` accepts a raw event mask, so producer correctness matters.

## Test Signals
Compile and link coverage across Panthor modules, ioctl submit tests, reservation update tests, firmware event simulation, reset/suspend sequencing, and fdinfo collection validate this API surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_trace.h

## Purpose
Defines Panthor tracepoints for GPU power-status transitions and job IRQ latency/event visibility.

## Important APIs, Types, and Functions
Trace system is `panthor`. `TRACE_EVENT_FN(gpu_power_status, ...)` records device name and shader/tiler/L2 power bitmaps and registers callbacks via `panthor_hw_power_status_register/unregister`. `TRACE_EVENT(gpu_job_irq, ...)` records firmware job IRQ event mask and handler duration in nanoseconds.

## Control Flow
When tracing is enabled, registration hooks can subscribe to hardware power-status updates. Job IRQ instrumentation emits a compact event after the IRQ handler has queued firmware events, letting developers distinguish interrupt dispatch latency from later workqueue processing.

## State and Persistence
Tracepoints persist only in the kernel tracing subsystem. They do not mutate driver state. Captured state is a snapshot of bitmaps, event masks, duration, and device name.

## Dependencies and Integration Points
Depends on Linux tracepoint infrastructure and `panthor_hw.h` callback hooks. Uses standard `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` pattern so exactly one translation unit can instantiate trace definitions.

## Risks and Edge Cases
Tracepoint field definitions must remain stable enough for tooling. The power tracepoint has registration side effects, so callback correctness matters. Job IRQ duration only covers the IRQ queuing path, not full firmware event processing.

## Test Signals
Build with tracing enabled, inspect generated trace events, enable `panthor:gpu_power_status` and `panthor:gpu_job_irq`, verify power bitmap updates and job IRQ duration/event masks during workload and runtime PM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/Kconfig

## Purpose
Defines the kernel configuration option for the DRM PL111 CLCD controller driver.

## Important APIs, Types, and Functions
Introduces `config DRM_PL111` as a tristate option titled "DRM Support for PL111 CLCD Controller". It depends on DRM, ARM/ARM64/COMPILE_TEST, optional VExpress config availability, and COMMON_CLK. It selects DRM client selection, KMS helper, GEM DMA helper, DRM bridge, and panel bridge support.

## Control Flow
Kconfig dependency resolution determines whether the driver can be built in, built as a module, or hidden. When enabled as a module, the help text states the module is `pl111_drm`.

## State and Persistence
No runtime state. The selected config persists in kernel `.config` and controls compilation of the PL111 object from the Makefile.

## Dependencies and Integration Points
Integrates the PL111 driver with DRM core, simple KMS helper usage, DMA GEM framebuffer allocation, bridge/panel display pipelines, common clock framework, and Arm platform support.

## Risks and Edge Cases
Dependency mistakes can expose the driver on platforms lacking clock or display bridge infrastructure. `VEXPRESS_CONFIG || VEXPRESS_CONFIG=n` allows builds when VExpress config is absent/disabled while avoiding incompatible enabled states.

## Test Signals
Signals are `allyesconfig`/`allmodconfig`/`COMPILE_TEST` coverage, module build as `pl111_drm`, and correct dependency selection for DRM helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/Makefile

## Purpose
Builds the PL111 DRM driver objects and conditionally includes variant/debugfs support.

## Important APIs, Types, and Functions
Defines `pl111_drm-y` with `pl111_display.o`, `pl111_versatile.o`, and `pl111_drv.o`. Adds `pl111_nomadik.o` when `CONFIG_ARCH_NOMADIK` is enabled and `pl111_debugfs.o` when `CONFIG_DEBUG_FS` is enabled. Connects `obj-$(CONFIG_DRM_PL111)` to `pl111_drm.o`.

## Control Flow
Kbuild collects the listed objects into the `pl111_drm` built-in or module target depending on `CONFIG_DRM_PL111`. Optional objects are compiled only when their config symbols are enabled.

## State and Persistence
No runtime state. Build state is encoded in generated object composition and module output.

## Dependencies and Integration Points
Integrates Kconfig with Kbuild. The required objects provide core driver, display pipe, and Versatile variant behavior; optional objects add Nomadik variant and debugfs register dump support.

## Risks and Edge Cases
Missing optional config guards would cause unresolved symbols or dead code. Debugfs support is excluded unless enabled, so declarations must match conditional build behavior elsewhere.

## Test Signals
Build matrix with `CONFIG_DRM_PL111=y/m`, `CONFIG_DEBUG_FS=y/n`, and `CONFIG_ARCH_NOMADIK=y/n` should produce the expected object composition without link errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_debugfs.c

## Purpose
Provides a debugfs register dump for the PL111 DRM driver.

## Important APIs, Types, and Functions
`pl111_reg_defs[]` maps selected CLCD register offsets to names. `pl111_debugfs_regs()` prints each register value with `seq_printf()`. `pl111_debugfs_init()` registers a single `regs` debugfs file through `drm_debugfs_create_files()`.

## Control Flow
When debugfs is enabled and the driver initializes its minor, `pl111_debugfs_init()` creates the file. Reading the file obtains the DRM device from `drm_info_node`, accesses `dev_private`, iterates the static register table, and reads MMIO offsets from `priv->regs`.

## State and Persistence
No persistent state. It exposes a live snapshot of hardware registers including timing, base addresses, control, IRQ enable/status/clear, and cursor registers.

## Dependencies and Integration Points
Depends on DRM debugfs/file helpers, seq_file, MMIO `readl()`, and register/private definitions from `pl111_drm.h`. It is conditionally built by the Makefile under `CONFIG_DEBUG_FS`.

## Risks and Edge Cases
Reads assume `priv->regs` remains valid while debugfs exists, which is tied to DRM device lifetime. Register lists are PL111-oriented and may not include all PL110/Nomadik-specific registers.

## Test Signals
With debugfs enabled, `/sys/kernel/debug/dri/*/regs` should exist for PL111 and show plausible values while modes are enabled/disabled. Build without debugfs should omit the object cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_display.c

## Purpose
Implements PL111 simple display pipe behavior: IRQ/vblank handling, mode validation, atomic check, enable/disable/update, pixel clock divider, format-to-control programming, and display pipe initialization.

## Important APIs, Types, and Functions
Public functions are `pl111_irq()` and `pl111_display_init()`. Internal display callbacks include `pl111_mode_valid()`, `pl111_display_check()`, `pl111_display_enable()`, `pl111_display_disable()`, `pl111_display_update()`, vblank enable/disable helpers, and `pl111_display_funcs`. Clock helpers implement `clk_ops` through `pl111_clk_div_choose_div()`, determine/recalc/set rate, and `pl111_init_clock_divider()`.

## Control Flow
IRQ handling reads masked IRQ status, handles `CLCD_IRQ_NEXTBASE_UPDATE` as vblank, clears IRQs, and returns handled status. Atomic check enforces 16-pixel horizontal granularity, dword-aligned framebuffer base, pitch equal to mode width times cpp, and mode changes for framebuffer format changes. Enable sets pixel clock, programs TIM0/TIM1/TIM2/TIM3 from mode timings and connector/bridge bus flags, selects grayscale/TFT mode, maps DRM formats to PL111/ST/PL110 control bits, enables LCD, waits for voltage stabilization, calls variant enable hook, powers LCD, and enables vblank if available. Update writes the upper base address and arms/sends page-flip events. Disable turns vblank off, powers down, waits, calls variant disable, clears control, and disables the clock.

## State and Persistence
Persistent state is in `pl111_drm_dev_private`: MMIO registers, selected control/IRQ offsets, connector/bridge/panel pointers, variant data/hooks, pixel clock/divider, and `tim2_lock`. Hardware state persists in CLCD timing/control/base/IRQ registers while enabled. CRTC event state is consumed on update.

## Dependencies and Integration Points
Depends on DRM simple KMS, GEM DMA framebuffer helpers, vblank/event handling, DRM format definitions, common clock framework, media bus formats, OF graph-discovered connector/bridge data, and PL111 private register definitions. Variant hooks allow board-specific display enable/disable and ST/PL110 bit routing.

## Risks and Edge Cases
TIM2 is shared between clock framework and display enable, requiring `tim2_lock`. Format routing differs between ARM PL110/PL111 and ST variants; BGR inversion is easy to regress. Broken clockdivider and broken vblank variants need fallback behavior. Bridge setup-time compensation toggles pixel clock edge. Pitch is constrained by absent pitch register. Bandwidth validation depends on `memory_bw` and default framebuffer depth.

## Test Signals
Signals include modeset on PL110/PL111/ST variants, vblank/page-flip events, framebuffer format matrix, grayscale bus format output, clock divider rate accuracy, bridge edge compensation, bandwidth rejection, suspend/disable power sequencing, and debugfs/timing register inspection after modeset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_drm.h

## Purpose
Defines PL111/PL110 register offsets, timing/control bitfields, variant metadata, driver private state, and display/debugfs/IRQ prototypes.

## Important APIs, Types, and Functions
Macro groups cover CLCD timing, framebuffer base, PL110/PL111 IRQ/control/cursor offsets, palette, TIM2 clock/polarity fields, control register pixel format/power/TFT/BGR bits, ST Micro extension bits, and `CLCD_IRQ_NEXTBASE_UPDATE`. Types are `pl111_variant_data` and `pl111_drm_dev_private`. Function declarations include `pl111_display_init()`, `pl111_irq()`, and `pl111_debugfs_init()`.

## Control Flow
Implementation files use `priv->ienb` and `priv->ctrl` to abstract PL110/PL111 register offset differences. Variant data drives format lists, broken clock/vblank handling, BGR routing, ST bitmux control, and default framebuffer depth. Display code stores connector/panel/bridge and variant callbacks in private state and programs registers through these definitions.

## State and Persistence
The private structure persists for the DRM device lifetime and holds MMIO base, memory bandwidth limit, clock/divider state, simple display pipe, bridge/panel/connector pointers, variant description, callbacks, and a `use_device_memory` flag. Register macros describe persistent hardware state programmed by display code.

## Dependencies and Integration Points
Depends on Linux clk provider and interrupt headers plus DRM bridge, connector, encoder, GEM, panel, and simple KMS helpers. It is included by PL111 display, debugfs, variant, and core driver files.

## Risks and Edge Cases
Register offset differences between PL110 and PL111 require correct `priv->ctrl`/`ienb` setup. Variant flags are tightly coupled to format/control programming. `tim2_lock` must cover shared clock divider and display timing writes. Debugfs declaration is unconditional while object inclusion is config-controlled, so call sites must be guarded appropriately.

## Test Signals
Compile all PL111 objects and variants, probe each supported variant, validate format lists and register programming, check vblank IRQ offset selection, and run debugfs builds with and without `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_drm.h -->
