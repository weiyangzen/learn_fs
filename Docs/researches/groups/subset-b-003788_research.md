# subset-b-003788 Research

Grouped research for Tegra host1x core, command submission, syncpoint/fence/interrupt handling, memory contexts, MIPI calibration, and generation-specific hardware register definitions. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/bus.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/bus.h

## Purpose

`bus.h` is the local declaration boundary for the Tegra host1x bus registration layer. It lets the host1x platform driver register and unregister a `struct host1x` controller and exposes the `host1x_bus_type` consumed by client-device code without pulling in implementation details.

## Important APIs, Types, And Functions

- `extern const struct bus_type host1x_bus_type`: the Linux bus type for host1x clients.
- `host1x_register(struct host1x *host1x)` and `host1x_unregister(struct host1x *host1x)`: controller lifecycle hooks called from `dev.c`.
- Forward declarations for `struct bus_type` and `struct host1x` keep this header lightweight.

## Control Flow

The header has no executable control flow. Runtime control is in the bus implementation: `host1x_probe()` calls `host1x_register()` after core resources are initialized, and remove/error paths call `host1x_unregister()`.

## State And Persistence Behavior

No state is stored here. The declared APIs mutate global Linux device-model state by registering host1x clients on `host1x_bus_type` and tracking a controller instance.

## Dependencies And Integration Points

It integrates `dev.c` with the host1x bus implementation and downstream DRM/media clients that bind to host1x children. The stable contract is the bus type plus register/unregister pair.

## Risks And Test Signals

The main risk is lifecycle ordering: bus registration must not expose clients before syncpoints, channels, interrupts, debugfs, and runtime PM are ready. Useful tests are host1x probe/remove, deferred-probe of child devices, and module unload with clients bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/bus.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.c

## Purpose

`cdma.c` implements the generic command-DMA queue for each host1x channel. It owns the circular pushbuffer, synchronizes producer submissions with hardware consumption, tracks submitted jobs in `sync_queue`, unpins buffers after syncpoint completion, and coordinates timeout recovery.

## Important APIs, Types, And Functions

- Pushbuffer helpers allocate WC memory, optionally map it through the host IOMMU, initialize the hardware restart word, and manage `pos`/`fence` circular slots.
- `host1x_cdma_init()` / `host1x_cdma_deinit()` initialize locks, completions, workqueue state, queue heads, pushbuffer storage, and timeout resources.
- `host1x_cdma_begin()`, `host1x_cdma_push()`, `host1x_cdma_push_wide()`, and `host1x_cdma_end()` are the submission sequence used by `channel_hw.c`.
- `host1x_cdma_wait_locked()` and `host1x_cdma_wait_pushbuffer_space()` sleep on either pushbuffer space or an empty sync queue while preserving the CDMA mutex contract.
- `update_cdma_locked()` consumes completed jobs, unpins their buffers, pops pushbuffer slots, drops job references, and wakes waiters.
- `host1x_cdma_update_sync_queue()` is the timeout recovery path that resumes at the next job or CPU-increments/cancels the failed syncpoint depending on `job->syncpt_recovery`.

## Control Flow

Submission enters with `host1x_cdma_begin()`, which holds `cdma->lock`, rejects locked syncpoints, initializes timeout work if needed, starts CDMA hardware if idle, and records the first GET offset. Callers then emit two-word or four-word opcodes into the circular pushbuffer. Wide pushes avoid splitting a four-word opcode pair across the restart word by inserting a restart/pad slot if needed. `host1x_cdma_end()` flushes the hardware PUT pointer, stores `first_get` and `num_slots` in the job, appends the job to `sync_queue`, starts the timeout timer on idle-to-active transitions, and unlocks.

Completion is asynchronous. Fence callbacks, timeout paths, and explicit updates schedule `cdma_update_work`, which calls `update_cdma_locked()`. That function walks the queue from the head until the first unfinished, non-cancelled job, then starts a timeout for that pending head. Finished jobs are unpinned and released in order because pushbuffer slots are also retired in FIFO order.

## State And Persistence Behavior

Persistent per-channel state includes the WC pushbuffer mapping, DMA/IOVA addresses, circular cursor fields, `sync_queue`, timeout metadata, `running`/`torndown`, and the current wait event. Job references persist while queued. Hardware state persists through channel DMA registers programmed by `cdma_hw.c`. IOMMU mappings for pushbuffer memory persist for the CDMA lifetime; gather/reloc mappings persist only until job unpin.

## Dependencies And Integration Points

This file depends on host1x hardware ops from `dev.h`, job pin/unpin, syncpoint expiration, tracepoints, Linux completions/workqueues, DMA/IOMMU APIs, and the channel container. It is driven primarily by `channel_hw.c` submission and by fence interrupts from `intr.c`/`fence.c`.

## Risks And Edge Cases

The pushbuffer full/empty convention is inverted from the sync queue, so cursor regressions can deadlock submitters. Wide opcode padding is required for HW6+ gather and stream-ID programming. Timeout recovery mutates queued commands for cancellation and relies on memory barriers before resuming hardware. CPU syncpoint recovery must only be used for jobs marked safe. `host1x_cdma_deinit()` refuses to destroy a running CDMA, so release paths need to stop channels first.

## Test Signals

Good signals include repeated submit/complete under high queue depth, pushbuffer wraparound, wide gather at the tail boundary, IOMMU and non-IOMMU pushbuffer allocation, timeout with recovery and without recovery, locked syncpoint rejection, module remove after idle, and trace output when `trace_cmdbuf` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.h

## Purpose

`cdma.h` defines the generic host1x command-DMA data structures and submission API shared by channel, hardware, timeout, and debug code.

## Important APIs, Types, And Functions

- `struct push_buffer`: mapped WC pushbuffer memory, DMA/physical addresses, circular `fence` and `pos`, and allocation sizes.
- `struct buffer_timeout`: delayed-work state plus the syncpoint/client expected to complete.
- `enum cdma_event`: wait reasons for an empty sync queue or pushbuffer space.
- `struct host1x_cdma`: lock, completion, event state, slot accounting, pushbuffer, FIFO `sync_queue`, timeout, running/teardown flags, and update work.
- Public APIs cover init/deinit, begin/push/push_wide/end, async update, waiting, timeout sync-queue repair, and debug peeking.

## Control Flow

The header documents the producer sequence `begin -> push -> end` and consumer `update` path. Implementations require callers to hold the CDMA lock for waits and most slot/cursor mutations.

## State And Persistence Behavior

The structures are embedded in `struct host1x_channel` and persist for the channel lifetime. Queued jobs and pushbuffer slots persist until syncpoint completion or timeout cancellation retires them.

## Dependencies And Integration Points

It depends on Linux mutex/completion/list/workqueue primitives and is included by `channel.h`, `cdma.c`, `cdma_hw.c`, and debug code. Container macros connect CDMA to its channel and host controller.

## Risks And Test Signals

Field invariants are cross-file contracts: `first_get`, `last_pos`, and `num_slots` must stay in units expected by hardware register code and debug decoding. Build tests catch signature drift; runtime tests should exercise wraparound, timeout, and channel release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.c

## Purpose

`channel.c` manages allocation, reference counting, and high-level submission entry for host1x channels. It owns the bitmap of allocated channel slots and bridges exported client APIs to SoC-specific channel/CDMA hardware operations.

## Important APIs, Types, And Functions

- `host1x_channel_list_init()` / `host1x_channel_list_free()` allocate the channel array and allocation bitmap.
- `host1x_channel_request()` selects a free channel, initializes its kref, submit mutex, client/device pointers, hardware registers, and CDMA queue.
- `host1x_channel_get()`, `host1x_channel_get_index()`, and `host1x_channel_put()` manage references.
- `host1x_job_submit()` exports submission and calls `host1x_hw_channel_submit()`.
- `host1x_channel_stop()` and `host1x_channel_stop_all()` stop CDMA on one or all allocated channels.

## Control Flow

Clients request channels through `host1x_channel_request()`. Allocation is serialized by `channel_list.lock`; the chosen bit is set before hardware/CDMA init. Submission is delegated to hardware-specific `channel_submit()` from `channel_hw.c`. Release goes through kref destruction, stops CDMA, deinitializes CDMA resources, and clears the bitmap bit.

## State And Persistence Behavior

State persists in `struct host1x_channel_list` and each `struct host1x_channel`: allocation bit, kref, ID, submit lock, MMIO base, client pointer, device pointer, and embedded CDMA state. Channel hardware remains programmed until stopped, reset, or reinitialized.

## Dependencies And Integration Points

This file integrates host1x bus clients with `dev.h` operation tables and CDMA. It exports symbols used by DRM/media client drivers and by debug/runtime PM paths.

## Risks And Test Signals

Failure after setting the allocation bit must clear it; release must not race with debug/status readers using `host1x_channel_get_index()`. Test signals include exhausting all channels, request failure injection, concurrent channel get/put, stop-all during runtime suspend, and submit after a timeout-locked syncpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.h

## Purpose

`channel.h` defines the host1x channel list and per-channel object embedded with a CDMA queue. It is the shared structural contract between allocation, hardware submission, debug, and runtime PM code.

## Important APIs, Types, And Functions

- `struct host1x_channel_list`: dynamically allocated channel array, mutex, and allocation bitmap.
- `struct host1x_channel`: kref, channel ID, submit mutex, register base, associated host1x client/device, and `struct host1x_cdma`.
- Prototypes expose list init/free, indexed lookup, and stop-all.

## Control Flow

There is no executable flow in the header. The lifecycle is allocate from list, initialize hardware and CDMA, submit jobs under `submitlock`, then release through kref.

## State And Persistence Behavior

The channel object persists while its kref is nonzero. Its MMIO base and CDMA queue represent hardware-facing state; `allocated_channels` is the allocator's source of truth.

## Dependencies And Integration Points

It includes Linux I/O, kref, mutex, and `cdma.h`; `dev.h`, `channel.c`, `channel_hw.c`, and debug code all rely on this layout.

## Risks And Test Signals

Because the CDMA object is embedded, channel release ordering must stop hardware before freeing CDMA mappings. Compile coverage and runtime channel allocation/submission/release tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.c

## Purpose

`context.c` implements host1x memory-context devices used for IOMMU-backed channel isolation. It creates one child device per `iommu-map` entry, configures DMA/IOMMU state for each, and allocates contexts to callers by PID and IOMMU device.

## Important APIs, Types, And Functions

- `host1x_memory_context_list_init()`: parses `iommu-map`, creates `host1x-ctx.N` devices on `host1x-context` bus, sets a 38-bit DMA mask, configures DMA/IOMMU with `of_dma_configure_id()`, and records stream IDs.
- `host1x_memory_context_list_free()`: unregisters context devices and frees the array.
- `host1x_memory_context_alloc()`: finds an existing context owned by the same PID or an unused compatible context, sets `owner`, and initializes/refcounts it.
- `host1x_memory_context_get()` / `host1x_memory_context_put()` manage references and clear the PID owner on last put.

## Control Flow

Probe-time initialization is optional: no `iommu-map` means zero contexts and success. When entries exist, each device is initialized, added, DMA-configured with the entry index as ID, and required to have an IOMMU mapping and stream ID. Allocation is serialized by the context-list mutex and matches contexts to the requesting device's IOMMU provider.

## State And Persistence Behavior

The context-list array persists for the host lifetime. Each context stores a child `struct device`, DMA mask/parameters, stream ID, owner PID, and refcount. Ownership persists across multiple allocations by the same PID until references are dropped.

## Dependencies And Integration Points

Depends on Open Firmware `iommu-map`, DMA/IOMMU APIs, `host1x_context_device_bus_type`, PID refcounting, and public `struct host1x_memory_context` from `<linux/host1x.h>`. It integrates with DRM Tegra UAPI and submit paths, which attach a memory context to jobs so HW6+ stream-ID commands can isolate engines.

## Risks And Test Signals

Probe fails if DT advertises contexts but IOMMU is disabled or stream IDs cannot be read. Context sharing is per PID and IOMMU device, so PID lifetime and refcount handling matter. Tests should cover no-context DT, valid contexts, IOMMU-disabled failure, allocation reuse by same PID, exhaustion returning `-EBUSY`, and submit stream-ID selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.h

## Purpose

`context.h` declares the host1x memory-context list and optional IOMMU-context lifecycle APIs. It lets `dev.c` initialize/free context devices while compiling to no-ops when `CONFIG_IOMMU_API` is disabled.

## Important APIs, Types, And Functions

- `extern struct bus_type host1x_context_device_bus_type`: bus used by context child devices.
- `struct host1x_memory_context_list`: mutex, dynamic context-device array, and length.
- `host1x_memory_context_list_init()` / `host1x_memory_context_list_free()` are real APIs under `CONFIG_IOMMU_API` and inline no-ops otherwise.

## Control Flow

No direct control flow exists in the header. The conditional compilation controls whether host1x probe actually creates IOMMU context devices.

## State And Persistence Behavior

The list state persists inside `struct host1x`. With IOMMU disabled, no context state is created and callers see unsupported behavior from public APIs.

## Dependencies And Integration Points

It includes mutex/refcount primitives and is included by `dev.h`, `context.c`, and submit paths via public host1x structures.

## Risks And Test Signals

The no-op stubs must match the real API signature. Build tests with and without `CONFIG_IOMMU_API`, plus probe on DT with and without `iommu-map`, are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context_bus.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/context_bus.c

## Purpose

`context_bus.c` defines and registers the Linux bus type used for host1x memory-context child devices.

## Important APIs, Types, And Functions

- `const struct bus_type host1x_context_device_bus_type = { .name = "host1x-context" }`.
- `host1x_context_device_bus_init()` registers the bus at `postcore_initcall` time.

## Control Flow

At postcore init, the bus is registered before the host1x platform driver creates context devices. Failure is logged and returned from the initcall.

## State And Persistence Behavior

The registered bus type persists globally for the kernel lifetime. Context devices created by `context.c` attach to this bus.

## Dependencies And Integration Points

It depends on Linux device core and exports the bus symbol for the context implementation. The ordering matters because `device_add()` in `context.c` expects the bus to exist.

## Risks And Test Signals

The bus has no match/probe callbacks, so it is purely a device-model grouping mechanism. Test signals are successful early registration, context-device creation under `/sys/bus/host1x-context`, and clean behavior if bus registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context_bus.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.c

## Purpose

`debug.c` implements host1x debugfs and printk dump support. It reports syncpoint state, waiters, mlocks, channel CDMA/FIFO state, and queued gathers, and exposes knobs for command-buffer tracing and timeout forcing.

## Important APIs, Types, And Functions

- `host1x_debug_output()` and `host1x_debug_cont()` format output through a generic `struct output`.
- `show_syncpts()` reads min/max values and counts fence waiters per syncpoint.
- `show_channel()` runtime-resumes the host, locks CDMA/debug locks, and delegates FIFO/CDMA decoding to hardware debug ops.
- `show_all()` prints mlocks, syncpoints, and all allocated channels.
- `host1x_debug_init()` / `host1x_debug_deinit()` create/remove debugfs files.
- `host1x_debug_dump()` writes the same full state to printk, used during timeout handling.

## Control Flow

Debugfs `status` and `status_all` call `show_all()` with FIFO disabled/enabled. Status collection resumes the device, locks enough state to avoid racing queue mutation, invokes hardware-specific decoders, and releases runtime PM. Timeout handling in `cdma_hw.c` calls `host1x_debug_dump()` before freezing a timed-out channel.

## State And Persistence Behavior

Persistent debug state includes the debugfs dentry, `host1x_debug_trace_cmdbuf`, and force-timeout variables. The output routines mostly observe hardware/software state but can load syncpoint registers into shadow values.

## Dependencies And Integration Points

Depends on debugfs, seq_file, runtime PM, channel/CDMA structures, syncpoint APIs, and hardware debug operation tables. Trace control integrates with `cdma.c` and `channel_hw.c`.

## Risks And Test Signals

Debug reads can fail if runtime resume fails. Hardware debug helpers must tolerate inactive channels and unmappable BOs. Tests should read debugfs during idle, active jobs, timeout, and suspend/resume, and verify no lockdep inversions among CDMA, debug, and syncpoint locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.h

## Purpose

`debug.h` declares the generic host1x debug output abstraction and debug lifecycle APIs.

## Important APIs, Types, And Functions

- `struct output`: callback context plus a 256-byte formatting buffer.
- `write_to_seqfile()` and `write_to_printk()` adapt output to debugfs or printk.
- `host1x_debug_output()` / `host1x_debug_cont()` are printf-style helpers.
- `host1x_debug_trace_cmdbuf` controls command-buffer trace emission.
- Init/deinit/dump prototypes are consumed by `dev.c` and timeout code.

## Control Flow

The inline writers either call `seq_write()` or `pr_info()`/`pr_cont()`. Higher-level flow is in `debug.c`.

## State And Persistence Behavior

The header stores no state except declaring the external trace flag. Output buffers are stack/local in callers.

## Dependencies And Integration Points

It depends on debugfs/seq_file/printk and is included by generic and hardware debug implementations plus CDMA tracing code.

## Risks And Test Signals

Format strings must fit the buffer or be intentionally truncated by `vsnprintf()`. Build coverage and debugfs reads during active hardware are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.c

## Purpose

`dev.c` is the Tegra host1x platform driver. It maps SoC resources, selects generation-specific operation tables, configures IOMMU/DMA behavior, initializes channels, contexts, syncpoints, interrupts, debugfs, runtime PM, child devices, virtualization tables, and module bus/driver registration.

## Important APIs, Types, And Functions

- MMIO helpers: `host1x_common_writel()`, hypervisor read/write, sync read/write/readq, and channel read/write.
- Static `host1x_info` tables describe Tegra20 through Tegra234 channel/syncpoint counts, sync register offsets, DMA masks, wide-gather support, hypervisor/common regions, stream-ID protection tables, and PM quirks.
- `host1x_setup_virtualization_tables()` programs SID offset/limit and VM access tables for hypervisor-capable SoCs.
- IOMMU helpers decide when host1x wants an IOMMU, attach a paging domain, initialize IOVA allocation, set the DMA mask, and detach/free on exit.
- `host1x_probe()` is the primary initialization pipeline; `host1x_remove()` tears it down.
- Runtime PM callbacks stop channels/interrupts, save/restore syncpoints, manage reset/clock state, and reprogram virtualization.

## Control Flow

Probe obtains match data, maps either legacy or VM/hypervisor/common register resources, collects named syncpoint IRQs with fallback to IRQ 0, initializes device lists and DMA parameters, calls the generation `init()` function, obtains clock/reset resources, initializes the BO cache and IOMMU, then channels, contexts, syncpoints, interrupts, debugfs, host1x bus registration, and child population. Every failure path unwinds the initialized subset in reverse order.

Runtime suspend stops CDMA on allocated channels, disables syncpoint interrupts, saves syncpoint state, optionally asserts resets, disables the clock, and releases reset controls. Runtime resume reacquires resets, enables the clock, deasserts reset, programs virtualization tables, restores syncpoints, and restarts interrupt hardware.

## State And Persistence Behavior

The `struct host1x` instance persists as platform data. It owns MMIO mappings, IRQ numbers, clocks/resets, IOMMU domain/IOVA allocator, operation-table pointers, syncpoints, channel/context lists, BO cache, debugfs root, and client-device list. Hardware state includes SID protection tables, VM permissions, syncpoint values, threshold interrupts, reset/clock state, and channel registers.

## Dependencies And Integration Points

Depends on Linux platform, OF, runtime PM, reset, clock, DMA/IOMMU/IOVA, tegra OPP, and host1x bus/client infrastructure. It includes generation headers `host1x01` through `host1x08`; child devices populated from DT are typically display, DRM, VIC, NVDEC, NVENC, and media clients.

## Risks And Edge Cases

IOMMU policy is SoC- and firewall-sensitive, especially for 32-bit gather limitations on Tegra124/210. Hypervisor resource names must match DT for newer SoCs. Runtime PM is intentionally forced active because dynamic RPM is not ready. SID table mistakes can break engine memory isolation. Probe unwinding spans many subsystems, so failure injection is valuable. `skip_reset_assert` preserves secure-world access on Tegra186 and must not regress.

## Test Signals

Signals include probe/remove for every compatible, DT resource validation, IOMMU and non-IOMMU boot, large-memory systems requiring 32-bit IOVA for old gathers, runtime suspend/resume, child device population, syncpoint IRQ delivery across multiple IRQ lines, virtualization-table programming on Tegra186/194/234, and module init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.h

## Purpose

`dev.h` is the central internal host1x device contract. It defines operation tables for each hardware block, SoC capability descriptors, the main `struct host1x`, MMIO helpers, and inline dispatch wrappers used by generic code.

## Important APIs, Types, And Functions

- Operation tables: `host1x_channel_ops`, `host1x_cdma_ops`, `host1x_pushbuffer_ops`, `host1x_debug_ops`, `host1x_syncpt_ops`, and `host1x_intr_ops`.
- SoC descriptors: `struct host1x_sid_entry`, `struct host1x_table_desc`, and `struct host1x_info`.
- `struct host1x`: persistent controller state including MMIO regions, IRQs, clock/reset, IOMMU domain/IOVA, operation pointers, syncpoints, channel/context lists, debugfs, device list, DMA parameters, and BO cache.
- Inline wrappers dispatch generic calls to the active generation's operation table for syncpoints, interrupts, channels, CDMA, pushbuffer, and debug.

## Control Flow

The header is not executable beyond inlines. Generation init code installs operation table pointers into `struct host1x`; generic code calls the wrappers without knowing which register layout is active.

## State And Persistence Behavior

`struct host1x` persists for the controller lifetime and is the root of almost all host1x state. Its operation pointers must be initialized before any channel/syncpoint/CDMA code runs.

## Dependencies And Integration Points

It includes Linux device/IOMMU/IOVA/IRQ/platform/reset headers and host1x internal headers. It is included by nearly every file in this subset and by generation include units.

## Risks And Test Signals

A missing operation pointer can crash through an inline wrapper. Capability fields must match DT and silicon. Build coverage across all generations, probe smoke tests, and static checks for initialized operation tables are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/fence.c

## Purpose

`fence.c` implements `dma_fence` objects backed by host1x syncpoint thresholds. It lets submitters and waiters use standard DMA fence semantics while completion is driven by host1x syncpoint threshold interrupts.

## Important APIs, Types, And Functions

- `host1x_fence_create(struct host1x_syncpt *sp, u32 threshold, bool timeout)`: allocates and initializes a fence for a syncpoint threshold.
- `host1x_syncpt_fence_enable_signaling()`: checks immediate expiration, takes interrupt/timeout references, optionally schedules a 30-second timeout, and queues the fence in interrupt state.
- `host1x_fence_signal()`: handles interrupt-side signaling, cancels timeout work, signals the base fence, and drops references.
- `do_fence_timeout()`: removes the fence from interrupt lists if still queued, marks `-ETIMEDOUT`, signals, and releases timeout/interrupt references.
- `host1x_fence_cancel()`: forces the timeout path synchronously.

## Control Flow

Fence users create a fence, then the DMA fence core calls `enable_signaling()` when a wait/callback needs interrupts. If the syncpoint is already expired, signaling is not enabled. Otherwise `intr.c` inserts it into the syncpoint's ordered fence list. Threshold IRQs call `host1x_fence_signal()` for expired entries. If timeout is enabled and no IRQ arrives, delayed work removes and signals the fence with an error.

## State And Persistence Behavior

Each fence stores a syncpoint pointer, threshold, timeout flag, delayed work, list node, and atomic `signaling` gate. References are deliberately held by interrupt and timeout paths to meet `dma_fence` lifetime rules. Fence-list state persists in `struct host1x_syncpt`.

## Dependencies And Integration Points

Depends on Linux `dma_fence`, sync files, delayed work, `intr.c`, and `syncpt.c`. Channel submission creates submit-complete fences; `host1x_syncpt_wait()` creates wait fences.

## Risks And Test Signals

The race between IRQ signaling and timeout cancellation is guarded by `atomic_xchg()` and reference rules; regressions can leak or double-put fences. Long-lasting fences are reaped after 30 seconds only when timeout is requested. Tests should cover already-expired thresholds, normal IRQ signaling, cancellation, timeout, callback removal during job free, and lockdep for fence-list spinlocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/fence.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/fence.h

## Purpose

`fence.h` defines the host1x syncpoint fence and per-syncpoint fence-list structures used by `fence.c` and `intr.c`.

## Important APIs, Types, And Functions

- `struct host1x_syncpt_fence`: embedded `dma_fence`, atomic signaling guard, syncpoint pointer, threshold, timeout flag, delayed timeout work, and list node.
- `struct host1x_fence_list`: spinlock plus ordered list of pending fences.
- `host1x_fence_signal()` is the interrupt-facing signal hook.

## Control Flow

The header has no direct flow. Fences are inserted under the list spinlock, signaled from threshold interrupts, or cancelled via delayed work.

## State And Persistence Behavior

Fence objects persist until all DMA fence references are dropped. Fence lists persist in each syncpoint.

## Dependencies And Integration Points

It relies on DMA fence, delayed work, list, and spinlock types through includers. It is included by syncpoint and interrupt code.

## Risks And Test Signals

The list node must be initialized/deleted exactly once per queueing cycle. Build tests and fence race tests validate this small but central contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/fence.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/cdma_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/cdma_hw.c

## Purpose

`hw/cdma_hw.c` provides the generation-specialized hardware implementation of CDMA operations included into each `host1x0N.c` build unit. It programs channel DMA registers, handles channel stop/freeze/resume, initializes timeout work, and implements timeout-specific MLOCK cleanup.

## Important APIs, Types, And Functions

- `push_buffer_init()` writes the RESTART opcode at the end of the pushbuffer.
- `cdma_start()`, `cdma_flush()`, and `cdma_stop()` program DMASTART/DMAPUT/DMAEND/DMACTRL and wait for queue drain.
- `cdma_timeout_restart()` restores DMAGET from a timeout recovery address and restarts DMA.
- `cdma_freeze()` stops command processing, stops CDMA, tears down the channel, and marks the CDMA torn down.
- `cdma_resume()` clears command-processor stop and restarts from a selected GET pointer.
- `cdma_timeout_handler()` dumps debug state, checks whether the syncpoint really timed out, freezes hardware, releases MLOCK if needed, and repairs the sync queue.

## Control Flow

Generic `cdma.c` calls these operations through `host1x_cdma_ops`. Start programs the circular pushbuffer base/end and initializes GET to PUT before enabling DMA. Stop waits for an empty sync queue before asserting DMASTOP. Timeout handling first freezes the command processor for a clean snapshot, verifies the syncpoint threshold is still incomplete, freezes/tears down the channel, releases any held MLOCK on Tegra234 classes, then delegates job-queue repair to `host1x_cdma_update_sync_queue()`.

## State And Persistence Behavior

Hardware state includes DMA pointers, DMACTRL, command-processor stop bits, channel teardown state, and common MLOCK registers on HW8. Software state mutates `cdma->running`, `cdma->torndown`, `last_pos`, and timeout initialization/client fields.

## Dependencies And Integration Points

This file relies on register macros supplied by the including generation hardware header and on `HOST1X_HW` for conditional code. It integrates with `cdma.c`, `debug.c`, syncpoint APIs, and channel timeout policy.

## Risks And Test Signals

Register offsets differ substantially before and after HW6; inclusion with the wrong hardware header would corrupt registers. Timeout MLOCK release is implemented only for specific Tegra234 engine classes and warns for unknown classes. Tests should cover start/flush/stop, timeout recovery, channel teardown/resume, 64-bit DMA register programming on HW6+, and class-specific MLOCK release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/cdma_hw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/channel_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/channel_hw.c

## Purpose

`hw/channel_hw.c` is the generation-specialized host1x channel submission engine. It converts pinned `host1x_job` command descriptors into pushbuffer opcodes, handles waits/gathers/setclass, programs stream IDs and MLOCK sequences on HW6+, creates completion fences, and starts CDMA.

## Important APIs, Types, And Functions

- `submit_wait()`, `submit_setclass()`, and `submit_gathers()` emit host1x opcodes for waits, stream-ID-aware class switches, and gather DMA.
- `synchronize_syncpt_base()` supports relative waits on older hardware with wait bases.
- `host1x_channel_set_streamid()` and `host1x_enable_gather_filter()` program stream ID/filtering for secure gather handling.
- `channel_program_cdma()` builds the full command sequence, with older-HW serialization/base handling and HW6+ MLOCK/stream-ID/idle-fence wrapping.
- `channel_submit()` is the operation-table submit callback, handling submit lock, CDMA begin/end, fence creation, and tracepoints.
- `host1x_channel_init()` computes each channel's MMIO base.

## Control Flow

Submission locks `submitlock`, sets channel stream ID, enables gather filtering, assigns the syncpoint to the channel, begins CDMA, and emits opcodes. On HW6+, absolute pre-fence waits are emitted with an invalid stream ID, engine MLOCK is acquired, an idle fence is inserted before switching to the real stream ID, work gathers are submitted, another idle fence is inserted, and MLOCK is released. Older hardware optionally serializes against the syncpoint's current max, synchronizes wait base, emits setclass, increments syncpoint max, and submits gathers. A fence is created before `host1x_cdma_end()` flushes hardware so a fast completion is not missed.

## State And Persistence Behavior

The function mutates channel registers, CDMA pushbuffer, syncpoint max values, job `syncpt_end`, job fence/callback fields, and syncpoint channel assignment. Hardware-visible stream IDs and gather filter bits persist until changed by later submissions or reset.

## Dependencies And Integration Points

Depends on opcodes, generated register headers, `cdma.c`, `job.c`, `fence.c`, `syncpt.c`, tracepoints, and Tegra IOMMU stream-ID helpers. It is included into each generation build unit with `HOST1X_HW` controlling code shape.

## Risks And Test Signals

The HW6+ MLOCK/stream-ID sequence is security-sensitive; incorrect ordering can let an engine access buffers under the wrong stream ID. Fence creation errors are warned but submit still returns success. 64-bit gather addresses require `GATHER_W` support. Tests should include pre-fence waits, relative waits, wide gathers above 4 GiB, stream-ID isolation, MLOCK release after timeout, and submit-complete fence callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/channel_hw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw.c

## Purpose

`hw/debug_hw.c` provides common command decoding and gather-dump helpers for host1x debug output, then includes either the pre-HW6 or HW6+ register-specific debug implementation.

## Important APIs, Types, And Functions

- `show_channel_command()` decodes host1x opcodes such as SETCLASS, INCR, NONINCR, MASK, IMM, RESTART, GATHER, stream-ID/payload/wide variants, and MLOCK extend opcodes.
- `show_gather()` prints decoded words from a mapped pushbuffer or gather buffer, following pushbuffer wrap at the restart word.
- `show_channel_gathers()` walks queued jobs and dumps their pushbuffer slots and gather command buffers.
- Conditional include selects `debug_hw_1x06.c` for `HOST1X_HW >= 6`, otherwise `debug_hw_1x01.c`.

## Control Flow

Hardware debug ops call into this shared decoder while `debug.c` holds CDMA/debug locks. The decoder tracks how many payload words follow an opcode and prints continuations until the command is complete. Gather dumps map BOs unless the job already has a firewall gather copy.

## State And Persistence Behavior

This file observes CDMA queues, pushbuffers, gather buffers, and register snapshots. It does not intentionally mutate state except through BO mapping side effects and output emission.

## Dependencies And Integration Points

Depends on generated opcode/register definitions, CDMA/job/channel structures, host1x BO mapping, and `struct output`. Included generation build units install the resulting `host1x_debug_ops`.

## Risks And Test Signals

Debug decoding must match opcode encodings used by `channel_hw.c`; otherwise timeout dumps mislead recovery. Address mismatch protection avoids dumping unrelated memory when physical addresses alias unexpectedly. Test signals are debugfs/status dumps for active older and newer hardware, wide opcode decoding, gather-copy firewall jobs, and unmappable BO handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x01.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x01.c

## Purpose

`debug_hw_1x01.c` implements register-specific debug output for pre-HW6 host1x generations. It reports channel CDMA state, command FIFO contents through sync-register peek controls, and MLOCK ownership.

## Important APIs, Types, And Functions

- `host1x_debug_show_channel_cdma()`: reads DMASTART/DMAEND/DMAPUT/DMAGET/DMACTRL plus CBREAD/CBSTAT, prints active/waiting status, and dumps queued gathers.
- `host1x_debug_show_channel_fifo()`: uses `CFPEEK_CTRL`, pointer, setup, and read registers to decode command FIFO entries.
- `host1x_debug_show_mlocks()`: reads each MLOCK owner register and reports channel, CPU, or unlocked state.

## Control Flow

The CDMA path first checks DMASTOP or missing pushbuffer mapping and returns inactive if true. Otherwise it interprets CBSTAT as either host wait-on-syncpoint, wait-on-syncpoint-base, or active class/offset. FIFO dumping enables peek for the channel, walks read pointer to write pointer with wrap, decodes opcodes, and disables peek afterward.

## State And Persistence Behavior

The file reads hardware registers and temporarily programs CFPEEK control. It does not mutate persistent CDMA/job state.

## Dependencies And Integration Points

It relies on old sync/channel register macros and the shared command decoder from `debug_hw.c`. It is included for `HOST1X_HW < 6`.

## Risks And Test Signals

Peek control must be disabled after use; stale peek state can affect later diagnostics. Field widths differ across old generations, so generated headers must be correct. Test by reading debugfs while channels are idle, waiting, active, and with MLOCKs held.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x01.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x06.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x06.c

## Purpose

`debug_hw_1x06.c` implements register-specific debug output for HW6+ host1x generations with VM/hypervisor register layouts and wider DMA addresses.

## Important APIs, Types, And Functions

- `host1x_debug_show_channel_cdma()`: reads 64-bit-capable DMA start/end registers, DMAPUT/DMAGET/DMACTRL, command processor offset/class, channel status, and queued gathers.
- `host1x_debug_show_channel_fifo()`: reads command FIFO status/data and, on HW6/HW7, uses hypervisor peek registers with SLCG override to dump FIFO contents.
- `host1x_debug_show_mlocks()`: currently a TODO for newer hardware.

## Control Flow

CDMA debug returns inactive when DMASTOP is set or no pushbuffer exists; otherwise it prints whether the channel is waiting in host1x class or active in another class. FIFO debug prints direct FIFO status/data and conditionally performs hypervisor FIFO peeking for generations where those registers exist.

## State And Persistence Behavior

The file observes channel and hypervisor registers. During FIFO peeking on HW6/HW7 it temporarily forces clock-gating override and then clears both peek control and override.

## Dependencies And Integration Points

It depends on VM/hypervisor register macros, `HOST1X_HW`, the shared decoder in `debug_hw.c`, and debugfs dump flow from `debug.c`.

## Risks And Test Signals

The TODO MLOCK dump means newer timeout diagnostics lack MLOCK ownership detail. Hypervisor peek register availability changes on HW8, so conditional code must match silicon. Test debugfs on Tegra186/194/234, including 64-bit DMA addresses and FIFO non-empty cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw_1x06.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x01.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x01.c

## Purpose

`host1x01.c` is the generation include unit for host1x01 (Tegra20/Tegra30). It binds the shared hardware implementations to this SoC generation by including the matching register specification, defining `HOST1X_HW 1`, and installing operation tables into `struct host1x`.

## Important APIs, Types, And Functions

- Includes `host1x01.h` and `host1x01_hardware.h` to select the correct register map.
- Includes shared implementation files `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c` under this generation's `HOST1X_HW` value.
- `host1x01_init(struct host1x *host)` assigns channel, CDMA, pushbuffer, syncpoint, interrupt, and debug operation tables.
- SoC capabilities in `dev.c` for this generation: 8 channels, 32 syncpoints, 16 mlocks, 8 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

During platform probe, `dev.c` calls the `init` function from the matched `host1x_info`. The init function is intentionally simple: it stores pointers to the static ops compiled from the included shared code and returns success. Subsequent generic code dispatches through the installed ops.

## State And Persistence Behavior

No persistent state is allocated here. The lasting effect is operation-table selection in the live `struct host1x`; those pointers determine all future channel, CDMA, syncpoint, interrupt, and debug register accesses.

## Dependencies And Integration Points

This file depends on the exact generated register headers for Tegra20/Tegra30. It integrates the generic host1x core with `dev.c` match data and is sensitive to all `#if HOST1X_HW` branches in shared hardware files.

## Risks And Test Signals

Including the wrong hardware header or using the wrong `HOST1X_HW` value would compile valid code that programs invalid registers. Test signals are boot/probe on Tegra20/Tegra30, channel submit, syncpoint interrupt delivery, suspend/resume, timeout recovery, and debugfs status for this generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x01.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x01.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x01.h

## Purpose

`host1x01.h` declares the host1x01 (Tegra20/Tegra30) generation initialization entry point used by the platform driver's match table.

## Important APIs, Types, And Functions

- Forward declaration of `struct host1x`.
- `int host1x01_init(struct host1x *host)`: installs hardware operation tables for Tegra20/Tegra30.
- Capability context from `dev.c`: 8 channels, 32 syncpoints, 16 mlocks, 8 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

The header has no executable control flow. `dev.c` references the prototype when building the `host1x_info` table, and the matching platform probe calls the function after mapping resources and before initializing channels/syncpoints.

## State And Persistence Behavior

No state is stored in this header. The declared function mutates operation-table pointers in `struct host1x`.

## Dependencies And Integration Points

It is paired with `host1x01.c` and included by `dev.c`. The function name is a cross-file contract for SoC match data.

## Risks And Test Signals

Signature drift breaks generation init at build time. Runtime validation is probe on Tegra20/Tegra30 and confirming that all operation pointers are non-NULL after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x01.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x01_hardware.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x01_hardware.h

## Purpose

`host1x01_hardware.h` is the hardware-register umbrella header for host1x01 (Tegra20/Tegra30). It gathers the generated register/field definitions and opcode helpers needed by the shared hardware implementation files.

## Important APIs, Types, And Functions

- Includes `hw_host1x01_channel.h`, `hw_host1x01_sync.h`, `hw_host1x01_uclass.h`, and `opcodes.h`.
- Provides the register macros consumed by `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c`.
- Layout focus: legacy channel and sync register blocks with generated inline field helpers.
- SoC capability context: 8 channels, 32 syncpoints, 16 mlocks, 8 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

There is no runtime control flow. The inclusion order determines which register names and field helpers are visible when the generation `.c` file includes shared hardware code.

## State And Persistence Behavior

No software state is stored. The macros describe hardware state that persists in MMIO registers after writes from the host1x driver.

## Dependencies And Integration Points

It depends on Linux type/bit helpers and the generated host1x register headers. It is included only through the matching `host1x01.c` generation unit.

## Risks And Test Signals

Omitting a register header causes compile failures; wrong offsets cause silent hardware misprogramming. Test signals include generation-specific build coverage, probe, channel DMA, syncpoint interrupts, debugfs dumps, and timeout recovery on Tegra20/Tegra30.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x01_hardware.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02.c

## Purpose

`host1x02.c` is the generation include unit for host1x02 (Tegra114). It binds the shared hardware implementations to this SoC generation by including the matching register specification, defining `HOST1X_HW 2`, and installing operation tables into `struct host1x`.

## Important APIs, Types, And Functions

- Includes `host1x02.h` and `host1x02_hardware.h` to select the correct register map.
- Includes shared implementation files `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c` under this generation's `HOST1X_HW` value.
- `host1x02_init(struct host1x *host)` assigns channel, CDMA, pushbuffer, syncpoint, interrupt, and debug operation tables.
- SoC capabilities in `dev.c` for this generation: 9 channels, 32 syncpoints, 16 mlocks, 12 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

During platform probe, `dev.c` calls the `init` function from the matched `host1x_info`. The init function is intentionally simple: it stores pointers to the static ops compiled from the included shared code and returns success. Subsequent generic code dispatches through the installed ops.

## State And Persistence Behavior

No persistent state is allocated here. The lasting effect is operation-table selection in the live `struct host1x`; those pointers determine all future channel, CDMA, syncpoint, interrupt, and debug register accesses.

## Dependencies And Integration Points

This file depends on the exact generated register headers for Tegra114. It integrates the generic host1x core with `dev.c` match data and is sensitive to all `#if HOST1X_HW` branches in shared hardware files.

## Risks And Test Signals

Including the wrong hardware header or using the wrong `HOST1X_HW` value would compile valid code that programs invalid registers. Test signals are boot/probe on Tegra114, channel submit, syncpoint interrupt delivery, suspend/resume, timeout recovery, and debugfs status for this generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02.h

## Purpose

`host1x02.h` declares the host1x02 (Tegra114) generation initialization entry point used by the platform driver's match table.

## Important APIs, Types, And Functions

- Forward declaration of `struct host1x`.
- `int host1x02_init(struct host1x *host)`: installs hardware operation tables for Tegra114.
- Capability context from `dev.c`: 9 channels, 32 syncpoints, 16 mlocks, 12 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

The header has no executable control flow. `dev.c` references the prototype when building the `host1x_info` table, and the matching platform probe calls the function after mapping resources and before initializing channels/syncpoints.

## State And Persistence Behavior

No state is stored in this header. The declared function mutates operation-table pointers in `struct host1x`.

## Dependencies And Integration Points

It is paired with `host1x02.c` and included by `dev.c`. The function name is a cross-file contract for SoC match data.

## Risks And Test Signals

Signature drift breaks generation init at build time. Runtime validation is probe on Tegra114 and confirming that all operation pointers are non-NULL after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02_hardware.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02_hardware.h

## Purpose

`host1x02_hardware.h` is the hardware-register umbrella header for host1x02 (Tegra114). It gathers the generated register/field definitions and opcode helpers needed by the shared hardware implementation files.

## Important APIs, Types, And Functions

- Includes `hw_host1x02_channel.h`, `hw_host1x02_sync.h`, `hw_host1x02_uclass.h`, and `opcodes.h`.
- Provides the register macros consumed by `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c`.
- Layout focus: legacy channel and sync register blocks with generated inline field helpers.
- SoC capability context: 9 channels, 32 syncpoints, 16 mlocks, 12 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

There is no runtime control flow. The inclusion order determines which register names and field helpers are visible when the generation `.c` file includes shared hardware code.

## State And Persistence Behavior

No software state is stored. The macros describe hardware state that persists in MMIO registers after writes from the host1x driver.

## Dependencies And Integration Points

It depends on Linux type/bit helpers and the generated host1x register headers. It is included only through the matching `host1x02.c` generation unit.

## Risks And Test Signals

Omitting a register header causes compile failures; wrong offsets cause silent hardware misprogramming. Test signals include generation-specific build coverage, probe, channel DMA, syncpoint interrupts, debugfs dumps, and timeout recovery on Tegra114.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x02_hardware.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x04.c

## Purpose

`host1x04.c` is the generation include unit for host1x04 (Tegra124). It binds the shared hardware implementations to this SoC generation by including the matching register specification, defining `HOST1X_HW 4`, and installing operation tables into `struct host1x`.

## Important APIs, Types, And Functions

- Includes `host1x04.h` and `host1x04_hardware.h` to select the correct register map.
- Includes shared implementation files `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c` under this generation's `HOST1X_HW` value.
- `host1x04_init(struct host1x *host)` assigns channel, CDMA, pushbuffer, syncpoint, interrupt, and debug operation tables.
- SoC capabilities in `dev.c` for this generation: 12 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

During platform probe, `dev.c` calls the `init` function from the matched `host1x_info`. The init function is intentionally simple: it stores pointers to the static ops compiled from the included shared code and returns success. Subsequent generic code dispatches through the installed ops.

## State And Persistence Behavior

No persistent state is allocated here. The lasting effect is operation-table selection in the live `struct host1x`; those pointers determine all future channel, CDMA, syncpoint, interrupt, and debug register accesses.

## Dependencies And Integration Points

This file depends on the exact generated register headers for Tegra124. It integrates the generic host1x core with `dev.c` match data and is sensitive to all `#if HOST1X_HW` branches in shared hardware files.

## Risks And Test Signals

Including the wrong hardware header or using the wrong `HOST1X_HW` value would compile valid code that programs invalid registers. Test signals are boot/probe on Tegra124, channel submit, syncpoint interrupt delivery, suspend/resume, timeout recovery, and debugfs status for this generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x04.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x04.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x04.h

## Purpose

`host1x04.h` declares the host1x04 (Tegra124) generation initialization entry point used by the platform driver's match table.

## Important APIs, Types, And Functions

- Forward declaration of `struct host1x`.
- `int host1x04_init(struct host1x *host)`: installs hardware operation tables for Tegra124.
- Capability context from `dev.c`: 12 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

The header has no executable control flow. `dev.c` references the prototype when building the `host1x_info` table, and the matching platform probe calls the function after mapping resources and before initializing channels/syncpoints.

## State And Persistence Behavior

No state is stored in this header. The declared function mutates operation-table pointers in `struct host1x`.

## Dependencies And Integration Points

It is paired with `host1x04.c` and included by `dev.c`. The function name is a cross-file contract for SoC match data.

## Risks And Test Signals

Signature drift breaks generation init at build time. Runtime validation is probe on Tegra124 and confirming that all operation pointers are non-NULL after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x04.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x04_hardware.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x04_hardware.h

## Purpose

`host1x04_hardware.h` is the hardware-register umbrella header for host1x04 (Tegra124). It gathers the generated register/field definitions and opcode helpers needed by the shared hardware implementation files.

## Important APIs, Types, And Functions

- Includes `hw_host1x04_channel.h`, `hw_host1x04_sync.h`, `hw_host1x04_uclass.h`, and `opcodes.h`.
- Provides the register macros consumed by `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c`.
- Layout focus: legacy channel and sync register blocks with generated inline field helpers.
- SoC capability context: 12 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

There is no runtime control flow. The inclusion order determines which register names and field helpers are visible when the generation `.c` file includes shared hardware code.

## State And Persistence Behavior

No software state is stored. The macros describe hardware state that persists in MMIO registers after writes from the host1x driver.

## Dependencies And Integration Points

It depends on Linux type/bit helpers and the generated host1x register headers. It is included only through the matching `host1x04.c` generation unit.

## Risks And Test Signals

Omitting a register header causes compile failures; wrong offsets cause silent hardware misprogramming. Test signals include generation-specific build coverage, probe, channel DMA, syncpoint interrupts, debugfs dumps, and timeout recovery on Tegra124.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x04_hardware.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05.c

## Purpose

`host1x05.c` is the generation include unit for host1x05 (Tegra210). It binds the shared hardware implementations to this SoC generation by including the matching register specification, defining `HOST1X_HW 5`, and installing operation tables into `struct host1x`.

## Important APIs, Types, And Functions

- Includes `host1x05.h` and `host1x05_hardware.h` to select the correct register map.
- Includes shared implementation files `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c` under this generation's `HOST1X_HW` value.
- `host1x05_init(struct host1x *host)` assigns channel, CDMA, pushbuffer, syncpoint, interrupt, and debug operation tables.
- SoC capabilities in `dev.c` for this generation: 14 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

During platform probe, `dev.c` calls the `init` function from the matched `host1x_info`. The init function is intentionally simple: it stores pointers to the static ops compiled from the included shared code and returns success. Subsequent generic code dispatches through the installed ops.

## State And Persistence Behavior

No persistent state is allocated here. The lasting effect is operation-table selection in the live `struct host1x`; those pointers determine all future channel, CDMA, syncpoint, interrupt, and debug register accesses.

## Dependencies And Integration Points

This file depends on the exact generated register headers for Tegra210. It integrates the generic host1x core with `dev.c` match data and is sensitive to all `#if HOST1X_HW` branches in shared hardware files.

## Risks And Test Signals

Including the wrong hardware header or using the wrong `HOST1X_HW` value would compile valid code that programs invalid registers. Test signals are boot/probe on Tegra210, channel submit, syncpoint interrupt delivery, suspend/resume, timeout recovery, and debugfs status for this generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05.h

## Purpose

`host1x05.h` declares the host1x05 (Tegra210) generation initialization entry point used by the platform driver's match table.

## Important APIs, Types, And Functions

- Forward declaration of `struct host1x`.
- `int host1x05_init(struct host1x *host)`: installs hardware operation tables for Tegra210.
- Capability context from `dev.c`: 14 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

The header has no executable control flow. `dev.c` references the prototype when building the `host1x_info` table, and the matching platform probe calls the function after mapping resources and before initializing channels/syncpoints.

## State And Persistence Behavior

No state is stored in this header. The declared function mutates operation-table pointers in `struct host1x`.

## Dependencies And Integration Points

It is paired with `host1x05.c` and included by `dev.c`. The function name is a cross-file contract for SoC match data.

## Risks And Test Signals

Signature drift breaks generation init at build time. Runtime validation is probe on Tegra210 and confirming that all operation pointers are non-NULL after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05_hardware.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05_hardware.h

## Purpose

`host1x05_hardware.h` is the hardware-register umbrella header for host1x05 (Tegra210). It gathers the generated register/field definitions and opcode helpers needed by the shared hardware implementation files.

## Important APIs, Types, And Functions

- Includes `hw_host1x05_channel.h`, `hw_host1x05_sync.h`, `hw_host1x05_uclass.h`, and `opcodes.h`.
- Provides the register macros consumed by `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c`.
- Layout focus: legacy channel and sync register blocks with generated inline field helpers.
- SoC capability context: 14 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

There is no runtime control flow. The inclusion order determines which register names and field helpers are visible when the generation `.c` file includes shared hardware code.

## State And Persistence Behavior

No software state is stored. The macros describe hardware state that persists in MMIO registers after writes from the host1x driver.

## Dependencies And Integration Points

It depends on Linux type/bit helpers and the generated host1x register headers. It is included only through the matching `host1x05.c` generation unit.

## Risks And Test Signals

Omitting a register header causes compile failures; wrong offsets cause silent hardware misprogramming. Test signals include generation-specific build coverage, probe, channel DMA, syncpoint interrupts, debugfs dumps, and timeout recovery on Tegra210.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x05_hardware.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06.c

## Purpose

`host1x06.c` is the generation include unit for host1x06 (Tegra186). It binds the shared hardware implementations to this SoC generation by including the matching register specification, defining `HOST1X_HW 6`, and installing operation tables into `struct host1x`.

## Important APIs, Types, And Functions

- Includes `host1x06.h` and `host1x06_hardware.h` to select the correct register map.
- Includes shared implementation files `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c` under this generation's `HOST1X_HW` value.
- `host1x06_init(struct host1x *host)` assigns channel, CDMA, pushbuffer, syncpoint, interrupt, and debug operation tables.
- SoC capabilities in `dev.c` for this generation: 63 channels, 576 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor registers, stream-ID protection.

## Control Flow

During platform probe, `dev.c` calls the `init` function from the matched `host1x_info`. The init function is intentionally simple: it stores pointers to the static ops compiled from the included shared code and returns success. Subsequent generic code dispatches through the installed ops.

## State And Persistence Behavior

No persistent state is allocated here. The lasting effect is operation-table selection in the live `struct host1x`; those pointers determine all future channel, CDMA, syncpoint, interrupt, and debug register accesses.

## Dependencies And Integration Points

This file depends on the exact generated register headers for Tegra186. It integrates the generic host1x core with `dev.c` match data and is sensitive to all `#if HOST1X_HW` branches in shared hardware files.

## Risks And Test Signals

Including the wrong hardware header or using the wrong `HOST1X_HW` value would compile valid code that programs invalid registers. Test signals are boot/probe on Tegra186, channel submit, syncpoint interrupt delivery, suspend/resume, timeout recovery, and debugfs status for this generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06.h

## Purpose

`host1x06.h` declares the host1x06 (Tegra186) generation initialization entry point used by the platform driver's match table.

## Important APIs, Types, And Functions

- Forward declaration of `struct host1x`.
- `int host1x06_init(struct host1x *host)`: installs hardware operation tables for Tegra186.
- Capability context from `dev.c`: 63 channels, 576 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor registers, stream-ID protection.

## Control Flow

The header has no executable control flow. `dev.c` references the prototype when building the `host1x_info` table, and the matching platform probe calls the function after mapping resources and before initializing channels/syncpoints.

## State And Persistence Behavior

No state is stored in this header. The declared function mutates operation-table pointers in `struct host1x`.

## Dependencies And Integration Points

It is paired with `host1x06.c` and included by `dev.c`. The function name is a cross-file contract for SoC match data.

## Risks And Test Signals

Signature drift breaks generation init at build time. Runtime validation is probe on Tegra186 and confirming that all operation pointers are non-NULL after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06_hardware.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06_hardware.h

## Purpose

`host1x06_hardware.h` is the hardware-register umbrella header for host1x06 (Tegra186). It gathers the generated register/field definitions and opcode helpers needed by the shared hardware implementation files.

## Important APIs, Types, And Functions

- Includes `hw_host1x06_channel.h`, `hw_host1x06_uclass.h`, `hw_host1x06_vm.h`, `hw_host1x06_hypervisor.h`, and `opcodes.h`.
- Provides the register macros consumed by `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c`.
- Layout focus: VM channel/sync registers plus hypervisor protection and FIFO-peek registers.
- SoC capability context: 63 channels, 576 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor registers, stream-ID protection.

## Control Flow

There is no runtime control flow. The inclusion order determines which register names and field helpers are visible when the generation `.c` file includes shared hardware code.

## State And Persistence Behavior

No software state is stored. The macros describe hardware state that persists in MMIO registers after writes from the host1x driver.

## Dependencies And Integration Points

It depends on Linux type/bit helpers and the generated host1x register headers. It is included only through the matching `host1x06.c` generation unit.

## Risks And Test Signals

Omitting a register header causes compile failures; wrong offsets cause silent hardware misprogramming. Test signals include generation-specific build coverage, probe, channel DMA, syncpoint interrupts, debugfs dumps, and timeout recovery on Tegra186.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06_hardware.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x07.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x07.c

## Purpose

`host1x07.c` is the generation include unit for host1x07 (Tegra194). It binds the shared hardware implementations to this SoC generation by including the matching register specification, defining `HOST1X_HW 7`, and installing operation tables into `struct host1x`.

## Important APIs, Types, And Functions

- Includes `host1x07.h` and `host1x07_hardware.h` to select the correct register map.
- Includes shared implementation files `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c` under this generation's `HOST1X_HW` value.
- `host1x07_init(struct host1x *host)` assigns channel, CDMA, pushbuffer, syncpoint, interrupt, and debug operation tables.
- SoC capabilities in `dev.c` for this generation: 63 channels, 704 syncpoints, 32 mlocks, wide gathers, 40-bit DMA, hypervisor registers, no wait bases.

## Control Flow

During platform probe, `dev.c` calls the `init` function from the matched `host1x_info`. The init function is intentionally simple: it stores pointers to the static ops compiled from the included shared code and returns success. Subsequent generic code dispatches through the installed ops.

## State And Persistence Behavior

No persistent state is allocated here. The lasting effect is operation-table selection in the live `struct host1x`; those pointers determine all future channel, CDMA, syncpoint, interrupt, and debug register accesses.

## Dependencies And Integration Points

This file depends on the exact generated register headers for Tegra194. It integrates the generic host1x core with `dev.c` match data and is sensitive to all `#if HOST1X_HW` branches in shared hardware files.

## Risks And Test Signals

Including the wrong hardware header or using the wrong `HOST1X_HW` value would compile valid code that programs invalid registers. Test signals are boot/probe on Tegra194, channel submit, syncpoint interrupt delivery, suspend/resume, timeout recovery, and debugfs status for this generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x07.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x07.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x07.h

## Purpose

`host1x07.h` declares the host1x07 (Tegra194) generation initialization entry point used by the platform driver's match table.

## Important APIs, Types, And Functions

- Forward declaration of `struct host1x`.
- `int host1x07_init(struct host1x *host)`: installs hardware operation tables for Tegra194.
- Capability context from `dev.c`: 63 channels, 704 syncpoints, 32 mlocks, wide gathers, 40-bit DMA, hypervisor registers, no wait bases.

## Control Flow

The header has no executable control flow. `dev.c` references the prototype when building the `host1x_info` table, and the matching platform probe calls the function after mapping resources and before initializing channels/syncpoints.

## State And Persistence Behavior

No state is stored in this header. The declared function mutates operation-table pointers in `struct host1x`.

## Dependencies And Integration Points

It is paired with `host1x07.c` and included by `dev.c`. The function name is a cross-file contract for SoC match data.

## Risks And Test Signals

Signature drift breaks generation init at build time. Runtime validation is probe on Tegra194 and confirming that all operation pointers are non-NULL after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x07.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x07_hardware.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x07_hardware.h

## Purpose

`host1x07_hardware.h` is the hardware-register umbrella header for host1x07 (Tegra194). It gathers the generated register/field definitions and opcode helpers needed by the shared hardware implementation files.

## Important APIs, Types, And Functions

- Includes `hw_host1x07_channel.h`, `hw_host1x07_uclass.h`, `hw_host1x07_vm.h`, `hw_host1x07_hypervisor.h`, and `opcodes.h`.
- Provides the register macros consumed by `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c`.
- Layout focus: VM channel/sync registers plus hypervisor protection and FIFO-peek registers.
- SoC capability context: 63 channels, 704 syncpoints, 32 mlocks, wide gathers, 40-bit DMA, hypervisor registers, no wait bases.

## Control Flow

There is no runtime control flow. The inclusion order determines which register names and field helpers are visible when the generation `.c` file includes shared hardware code.

## State And Persistence Behavior

No software state is stored. The macros describe hardware state that persists in MMIO registers after writes from the host1x driver.

## Dependencies And Integration Points

It depends on Linux type/bit helpers and the generated host1x register headers. It is included only through the matching `host1x07.c` generation unit.

## Risks And Test Signals

Omitting a register header causes compile failures; wrong offsets cause silent hardware misprogramming. Test signals include generation-specific build coverage, probe, channel DMA, syncpoint interrupts, debugfs dumps, and timeout recovery on Tegra194.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x07_hardware.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x08.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x08.c

## Purpose

`host1x08.c` is the generation include unit for host1x08 (Tegra234). It binds the shared hardware implementations to this SoC generation by including the matching register specification, defining `HOST1X_HW 8`, and installing operation tables into `struct host1x`.

## Important APIs, Types, And Functions

- Includes `host1x08.h` and `host1x08_hardware.h` to select the correct register map.
- Includes shared implementation files `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c` under this generation's `HOST1X_HW` value.
- `host1x08_init(struct host1x *host)` assigns channel, CDMA, pushbuffer, syncpoint, interrupt, and debug operation tables.
- SoC capabilities in `dev.c` for this generation: 63 channels, 1024 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor/common registers, VM routing tables.

## Control Flow

During platform probe, `dev.c` calls the `init` function from the matched `host1x_info`. The init function is intentionally simple: it stores pointers to the static ops compiled from the included shared code and returns success. Subsequent generic code dispatches through the installed ops.

## State And Persistence Behavior

No persistent state is allocated here. The lasting effect is operation-table selection in the live `struct host1x`; those pointers determine all future channel, CDMA, syncpoint, interrupt, and debug register accesses.

## Dependencies And Integration Points

This file depends on the exact generated register headers for Tegra234. It integrates the generic host1x core with `dev.c` match data and is sensitive to all `#if HOST1X_HW` branches in shared hardware files.

## Risks And Test Signals

Including the wrong hardware header or using the wrong `HOST1X_HW` value would compile valid code that programs invalid registers. Test signals are boot/probe on Tegra234, channel submit, syncpoint interrupt delivery, suspend/resume, timeout recovery, and debugfs status for this generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x08.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x08.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x08.h

## Purpose

`host1x08.h` declares the host1x08 (Tegra234) generation initialization entry point used by the platform driver's match table.

## Important APIs, Types, And Functions

- Forward declaration of `struct host1x`.
- `int host1x08_init(struct host1x *host)`: installs hardware operation tables for Tegra234.
- Capability context from `dev.c`: 63 channels, 1024 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor/common registers, VM routing tables.

## Control Flow

The header has no executable control flow. `dev.c` references the prototype when building the `host1x_info` table, and the matching platform probe calls the function after mapping resources and before initializing channels/syncpoints.

## State And Persistence Behavior

No state is stored in this header. The declared function mutates operation-table pointers in `struct host1x`.

## Dependencies And Integration Points

It is paired with `host1x08.c` and included by `dev.c`. The function name is a cross-file contract for SoC match data.

## Risks And Test Signals

Signature drift breaks generation init at build time. Runtime validation is probe on Tegra234 and confirming that all operation pointers are non-NULL after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x08.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x08_hardware.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x08_hardware.h

## Purpose

`host1x08_hardware.h` is the hardware-register umbrella header for host1x08 (Tegra234). It gathers the generated register/field definitions and opcode helpers needed by the shared hardware implementation files.

## Important APIs, Types, And Functions

- Includes `hw_host1x08_uclass.h`, `hw_host1x08_vm.h`, `hw_host1x08_hypervisor.h`, `hw_host1x08_common.h`, and `opcodes.h`.
- Provides the register macros consumed by `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c`.
- Layout focus: VM registers, hypervisor protection registers, and common MLOCK registers.
- SoC capability context: 63 channels, 1024 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor/common registers, VM routing tables.

## Control Flow

There is no runtime control flow. The inclusion order determines which register names and field helpers are visible when the generation `.c` file includes shared hardware code.

## State And Persistence Behavior

No software state is stored. The macros describe hardware state that persists in MMIO registers after writes from the host1x driver.

## Dependencies And Integration Points

It depends on Linux type/bit helpers and the generated host1x register headers. It is included only through the matching `host1x08.c` generation unit.

## Risks And Test Signals

Omitting a register header causes compile failures; wrong offsets cause silent hardware misprogramming. Test signals include generation-specific build coverage, probe, channel DMA, syncpoint interrupts, debugfs dumps, and timeout recovery on Tegra234.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x08_hardware.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x01_channel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x01_channel.h

## Purpose

`hw_host1x01_channel.h` defines channel-local CDMA and FIFO registers for host1x01 (Tegra20/Tegra30). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: DMASTART/DMAPUT/DMAGET/DMAEND/DMACTRL, FIFO status, optional channel control or SMMU stream-ID offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 8 channels, 32 syncpoints, 16 mlocks, 8 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `cdma_hw.c`, `channel_hw.c`, and hardware debug code. The header is selected through `host1x01_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x01, probe on Tegra20/Tegra30, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x01_channel.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x01_sync.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x01_sync.h

## Purpose

`hw_host1x01_sync.h` defines legacy syncpoint, threshold interrupt, command FIFO peek, wait-base, CPU-increment, and MLOCK owner registers for host1x01 (Tegra20/Tegra30). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: SYNCPT, threshold status/enable/disable, CFPEEK, CBREAD/CBSTAT, SYNCPT_BASE, SYNCPT_CPU_INCR, and MLOCK owner field helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 8 channels, 32 syncpoints, 16 mlocks, 8 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `syncpt_hw.c`, `intr_hw.c`, `debug_hw_1x01.c`, and runtime PM save/restore. The header is selected through `host1x01_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x01, probe on Tegra20/Tegra30, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x01_sync.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x01_uclass.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x01_uclass.h

## Purpose

`hw_host1x01_uclass.h` defines host1x class register offsets and payload field encoders used inside pushbuffer opcodes for host1x01 (Tegra20/Tegra30). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: INCR_SYNCPT, WAIT_SYNCPT, WAIT_SYNCPT_BASE, LOAD_SYNCPT_BASE, INDOFF, LOAD_SYNCPT_PAYLOAD_32, and WAIT_SYNCPT_32 helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 8 channels, 32 syncpoints, 16 mlocks, 8 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `opcodes.h`, `channel_hw.c`, command firewall/debug decoding, and client command streams. The header is selected through `host1x01_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x01, probe on Tegra20/Tegra30, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x01_uclass.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x02_channel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x02_channel.h

## Purpose

`hw_host1x02_channel.h` defines channel-local CDMA and FIFO registers for host1x02 (Tegra114). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: DMASTART/DMAPUT/DMAGET/DMAEND/DMACTRL, FIFO status, optional channel control or SMMU stream-ID offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 9 channels, 32 syncpoints, 16 mlocks, 12 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `cdma_hw.c`, `channel_hw.c`, and hardware debug code. The header is selected through `host1x02_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x02, probe on Tegra114, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x02_channel.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x02_sync.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x02_sync.h

## Purpose

`hw_host1x02_sync.h` defines legacy syncpoint, threshold interrupt, command FIFO peek, wait-base, CPU-increment, and MLOCK owner registers for host1x02 (Tegra114). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: SYNCPT, threshold status/enable/disable, CFPEEK, CBREAD/CBSTAT, SYNCPT_BASE, SYNCPT_CPU_INCR, and MLOCK owner field helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 9 channels, 32 syncpoints, 16 mlocks, 12 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `syncpt_hw.c`, `intr_hw.c`, `debug_hw_1x01.c`, and runtime PM save/restore. The header is selected through `host1x02_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x02, probe on Tegra114, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x02_sync.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x02_uclass.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x02_uclass.h

## Purpose

`hw_host1x02_uclass.h` defines host1x class register offsets and payload field encoders used inside pushbuffer opcodes for host1x02 (Tegra114). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: INCR_SYNCPT, WAIT_SYNCPT, WAIT_SYNCPT_BASE, LOAD_SYNCPT_BASE, INDOFF, LOAD_SYNCPT_PAYLOAD_32, and WAIT_SYNCPT_32 helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 9 channels, 32 syncpoints, 16 mlocks, 12 wait bases, 32-bit DMA, legacy sync offset 0x3000.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `opcodes.h`, `channel_hw.c`, command firewall/debug decoding, and client command streams. The header is selected through `host1x02_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x02, probe on Tegra114, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x02_uclass.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x04_channel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x04_channel.h

## Purpose

`hw_host1x04_channel.h` defines channel-local CDMA and FIFO registers for host1x04 (Tegra124). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: DMASTART/DMAPUT/DMAGET/DMAEND/DMACTRL, FIFO status, optional channel control or SMMU stream-ID offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 12 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `cdma_hw.c`, `channel_hw.c`, and hardware debug code. The header is selected through `host1x04_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x04, probe on Tegra124, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x04_channel.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x04_sync.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x04_sync.h

## Purpose

`hw_host1x04_sync.h` defines legacy syncpoint, threshold interrupt, command FIFO peek, wait-base, CPU-increment, and MLOCK owner registers for host1x04 (Tegra124). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: SYNCPT, threshold status/enable/disable, CFPEEK, CBREAD/CBSTAT, SYNCPT_BASE, SYNCPT_CPU_INCR, and MLOCK owner field helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 12 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `syncpt_hw.c`, `intr_hw.c`, `debug_hw_1x01.c`, and runtime PM save/restore. The header is selected through `host1x04_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x04, probe on Tegra124, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x04_sync.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x04_uclass.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x04_uclass.h

## Purpose

`hw_host1x04_uclass.h` defines host1x class register offsets and payload field encoders used inside pushbuffer opcodes for host1x04 (Tegra124). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: INCR_SYNCPT, WAIT_SYNCPT, WAIT_SYNCPT_BASE, LOAD_SYNCPT_BASE, INDOFF, LOAD_SYNCPT_PAYLOAD_32, and WAIT_SYNCPT_32 helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 12 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `opcodes.h`, `channel_hw.c`, command firewall/debug decoding, and client command streams. The header is selected through `host1x04_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x04, probe on Tegra124, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x04_uclass.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_channel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_channel.h

## Purpose

`hw_host1x05_channel.h` defines channel-local CDMA and FIFO registers for host1x05 (Tegra210). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: DMASTART/DMAPUT/DMAGET/DMAEND/DMACTRL, FIFO status, optional channel control or SMMU stream-ID offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 14 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `cdma_hw.c`, `channel_hw.c`, and hardware debug code. The header is selected through `host1x05_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x05, probe on Tegra210, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_channel.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_sync.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_sync.h

## Purpose

`hw_host1x05_sync.h` defines legacy syncpoint, threshold interrupt, command FIFO peek, wait-base, CPU-increment, and MLOCK owner registers for host1x05 (Tegra210). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: SYNCPT, threshold status/enable/disable, CFPEEK, CBREAD/CBSTAT, SYNCPT_BASE, SYNCPT_CPU_INCR, and MLOCK owner field helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 14 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `syncpt_hw.c`, `intr_hw.c`, `debug_hw_1x01.c`, and runtime PM save/restore. The header is selected through `host1x05_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x05, probe on Tegra210, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_sync.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_uclass.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_uclass.h

## Purpose

`hw_host1x05_uclass.h` defines host1x class register offsets and payload field encoders used inside pushbuffer opcodes for host1x05 (Tegra210). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: INCR_SYNCPT, WAIT_SYNCPT, WAIT_SYNCPT_BASE, LOAD_SYNCPT_BASE, INDOFF, LOAD_SYNCPT_PAYLOAD_32, and WAIT_SYNCPT_32 helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 14 channels, 192 syncpoints, 16 mlocks, 64 wait bases, 34-bit DMA, sync offset 0x2100.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `opcodes.h`, `channel_hw.c`, command firewall/debug decoding, and client command streams. The header is selected through `host1x05_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x05, probe on Tegra210, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x05_uclass.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_channel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_channel.h

## Purpose

`hw_host1x06_channel.h` defines channel-local CDMA and FIFO registers for host1x06 (Tegra186). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: DMASTART/DMAPUT/DMAGET/DMAEND/DMACTRL, FIFO status, optional channel control or SMMU stream-ID offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 576 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor registers, stream-ID protection.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `cdma_hw.c`, `channel_hw.c`, and hardware debug code. The header is selected through `host1x06_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x06, probe on Tegra186, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_channel.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_hypervisor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_hypervisor.h

## Purpose

`hw_host1x06_hypervisor.h` defines hypervisor-visible protection, gather-filter, and command FIFO peek registers for host1x06 (Tegra186). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: SYNCPT_PROT_EN, CH_KERNEL_FILTER_GBUFFER, optional CMDFIFO peek controls, ICG override, and HW8 MLOCK enable offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 576 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor registers, stream-ID protection.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `dev.c`, `channel_hw.c`, `syncpt_hw.c`, and `debug_hw_1x06.c`. The header is selected through `host1x06_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x06, probe on Tegra186, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_hypervisor.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_uclass.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_uclass.h

## Purpose

`hw_host1x06_uclass.h` defines host1x class register offsets and payload field encoders used inside pushbuffer opcodes for host1x06 (Tegra186). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: INCR_SYNCPT, WAIT_SYNCPT, WAIT_SYNCPT_BASE, LOAD_SYNCPT_BASE, INDOFF, LOAD_SYNCPT_PAYLOAD_32, and WAIT_SYNCPT_32 helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 576 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor registers, stream-ID protection.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `opcodes.h`, `channel_hw.c`, command firewall/debug decoding, and client command streams. The header is selected through `host1x06_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x06, probe on Tegra186, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_uclass.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_vm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_vm.h

## Purpose

`hw_host1x06_vm.h` defines HW6+ VM register layout for channel DMA, command FIFO, syncpoint, threshold interrupt, and syncpoint-channel assignment for host1x06 (Tegra186). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: 64-bit DMA pointer registers, CMDFIFO status/data, CMDPROC_STOP, TEARDOWN, syncpoint CPU increment/status/threshold, interrupt destination where present, and channel assignment fields.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 576 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor registers, stream-ID protection.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `cdma_hw.c`, `channel_hw.c`, `intr_hw.c`, `syncpt_hw.c`, and `debug_hw_1x06.c`. The header is selected through `host1x06_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x06, probe on Tegra186, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x06_vm.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_channel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_channel.h

## Purpose

`hw_host1x07_channel.h` defines channel-local CDMA and FIFO registers for host1x07 (Tegra194). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: DMASTART/DMAPUT/DMAGET/DMAEND/DMACTRL, FIFO status, optional channel control or SMMU stream-ID offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 704 syncpoints, 32 mlocks, wide gathers, 40-bit DMA, hypervisor registers, no wait bases.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `cdma_hw.c`, `channel_hw.c`, and hardware debug code. The header is selected through `host1x07_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x07, probe on Tegra194, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_channel.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_hypervisor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_hypervisor.h

## Purpose

`hw_host1x07_hypervisor.h` defines hypervisor-visible protection, gather-filter, and command FIFO peek registers for host1x07 (Tegra194). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: SYNCPT_PROT_EN, CH_KERNEL_FILTER_GBUFFER, optional CMDFIFO peek controls, ICG override, and HW8 MLOCK enable offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 704 syncpoints, 32 mlocks, wide gathers, 40-bit DMA, hypervisor registers, no wait bases.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `dev.c`, `channel_hw.c`, `syncpt_hw.c`, and `debug_hw_1x06.c`. The header is selected through `host1x07_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x07, probe on Tegra194, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_hypervisor.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_uclass.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_uclass.h

## Purpose

`hw_host1x07_uclass.h` defines host1x class register offsets and payload field encoders used inside pushbuffer opcodes for host1x07 (Tegra194). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: INCR_SYNCPT, WAIT_SYNCPT, WAIT_SYNCPT_BASE, LOAD_SYNCPT_BASE, INDOFF, LOAD_SYNCPT_PAYLOAD_32, and WAIT_SYNCPT_32 helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 704 syncpoints, 32 mlocks, wide gathers, 40-bit DMA, hypervisor registers, no wait bases.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `opcodes.h`, `channel_hw.c`, command firewall/debug decoding, and client command streams. The header is selected through `host1x07_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x07, probe on Tegra194, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_uclass.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_vm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_vm.h

## Purpose

`hw_host1x07_vm.h` defines HW6+ VM register layout for channel DMA, command FIFO, syncpoint, threshold interrupt, and syncpoint-channel assignment for host1x07 (Tegra194). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: 64-bit DMA pointer registers, CMDFIFO status/data, CMDPROC_STOP, TEARDOWN, syncpoint CPU increment/status/threshold, interrupt destination where present, and channel assignment fields.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 704 syncpoints, 32 mlocks, wide gathers, 40-bit DMA, hypervisor registers, no wait bases.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `cdma_hw.c`, `channel_hw.c`, `intr_hw.c`, `syncpt_hw.c`, and `debug_hw_1x06.c`. The header is selected through `host1x07_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x07, probe on Tegra194, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x07_vm.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_channel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_channel.h

## Purpose

`hw_host1x08_channel.h` defines channel-local CDMA and FIFO registers for host1x08 (Tegra234). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: DMASTART/DMAPUT/DMAGET/DMAEND/DMACTRL, FIFO status, optional channel control or SMMU stream-ID offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 1024 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor/common registers, VM routing tables.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `cdma_hw.c`, `channel_hw.c`, and hardware debug code. The header is selected through `host1x08_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x08, probe on Tegra234, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_channel.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_common.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_common.h

## Purpose

`hw_host1x08_common.h` defines Tegra234 common-region MLOCK ownership/release registers for engines for host1x08 (Tegra234). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: OFA, NVJPG1, VIC, NVENC, NVDEC, and NVJPG MLOCK offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 1024 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor/common registers, VM routing tables.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `cdma_hw.c` timeout MLOCK release. The header is selected through `host1x08_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x08, probe on Tegra234, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_common.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_hypervisor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_hypervisor.h

## Purpose

`hw_host1x08_hypervisor.h` defines hypervisor-visible protection, gather-filter, and command FIFO peek registers for host1x08 (Tegra234). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: SYNCPT_PROT_EN, CH_KERNEL_FILTER_GBUFFER, optional CMDFIFO peek controls, ICG override, and HW8 MLOCK enable offsets.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 1024 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor/common registers, VM routing tables.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `dev.c`, `channel_hw.c`, `syncpt_hw.c`, and `debug_hw_1x06.c`. The header is selected through `host1x08_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x08, probe on Tegra234, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_hypervisor.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_uclass.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_uclass.h

## Purpose

`hw_host1x08_uclass.h` defines host1x class register offsets and payload field encoders used inside pushbuffer opcodes for host1x08 (Tegra234). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: INCR_SYNCPT, WAIT_SYNCPT, WAIT_SYNCPT_BASE, LOAD_SYNCPT_BASE, INDOFF, LOAD_SYNCPT_PAYLOAD_32, and WAIT_SYNCPT_32 helpers.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 1024 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor/common registers, VM routing tables.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `opcodes.h`, `channel_hw.c`, command firewall/debug decoding, and client command streams. The header is selected through `host1x08_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x08, probe on Tegra234, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_uclass.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_vm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_vm.h

## Purpose

`hw_host1x08_vm.h` defines HW6+ VM register layout for channel DMA, command FIFO, syncpoint, threshold interrupt, and syncpoint-channel assignment for host1x08 (Tegra234). It is a generated-style hardware ABI header consumed by the shared host1x hardware implementation.

## Important APIs, Types, And Functions

- Main definitions: 64-bit DMA pointer registers, CMDFIFO status/data, CMDPROC_STOP, TEARDOWN, syncpoint CPU increment/status/threshold, interrupt destination where present, and channel assignment fields.
- Naming convention exposes `_r` register offsets, `_f` field encoders, `_v` field extractors, and direct `HOST1X_*` macros where appropriate.
- SoC capability context: 63 channels, 1024 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor/common registers, VM routing tables.

## Control Flow

The header has no executable flow beyond inline field helpers. Runtime code uses these macros to build MMIO offsets, encode register values, decode status fields, and construct pushbuffer payloads.

## State And Persistence Behavior

No software state is stored. The definitions describe hardware state that persists in channel, sync, VM, hypervisor, or common MMIO windows until changed by later writes, reset, or runtime PM restore.

## Dependencies And Integration Points

Primary users are `cdma_hw.c`, `channel_hw.c`, `intr_hw.c`, `syncpt_hw.c`, and `debug_hw_1x06.c`. The header is selected through `host1x08_hardware.h` and therefore must match the `HOST1X_HW` compile-time branch in the including generation unit.

## Risks And Edge Cases

These offsets and masks are silicon contracts. Small field-width differences affect FIFO peeking, syncpoint interrupt scanning, stream-ID isolation, MLOCK release, and command encoding. The repeated generated macro style makes copy/paste mistakes hard to notice without hardware tests.

## Test Signals

Useful signals are compile coverage for host1x08, probe on Tegra234, syncpoint increment/interrupt tests, channel submit and timeout recovery, debugfs FIFO/CDMA dumps, stream-ID protection tests where applicable, and suspend/resume restore of register-backed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/hw_host1x08_vm.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/intr_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/intr_hw.c

## Purpose

`hw/intr_hw.c` implements syncpoint threshold interrupt hardware operations for each host1x generation. It disables/enables threshold interrupts, programs thresholds, services IRQ status bits, and initializes host-sync timing/destination registers.

## Important APIs, Types, And Functions

- `syncpt_thresh_isr()`: IRQ handler that scans status registers and calls `host1x_intr_handle_interrupt()` for set syncpoint bits.
- `process_32_syncpts()`: disables and acknowledges a 32-bit status group before dispatching each set bit.
- `host1x_intr_disable_all_syncpt_intrs()`: disables and clears all syncpoint threshold interrupt groups.
- `host1x_intr_init_host_sync()`: programs old host sync timing registers and, on HW8, syncpoint interrupt destination routing.
- `host1x_intr_set_syncpt_threshold()`, enable, and disable functions are operation-table callbacks.

## Control Flow

The ISR scans different register widths depending on architecture and generation: 32-bit loops on non-64-bit builds, special unaligned handling for Tegra186/194, and 64-bit status reads where supported. For each pending bit it disables/acks the hardware bit and lets generic interrupt code load the syncpoint and signal expired fences. Start-time initialization disables old write-drop timeouts on pre-HW6 and routes HW8 groups round-robin across VM IRQ lines.

## State And Persistence Behavior

Interrupt enable bits, status bits, threshold registers, host timing registers, and HW8 destination registers persist in hardware. Generic fence lists decide whether an interrupt is re-enabled after handling.

## Dependencies And Integration Points

Depends on generated sync/VM register macros, `host1x_intr_handle_interrupt()`, and `host1x_intr_ops` dispatch from `dev.h`. It is installed by generation init units.

## Risks And Test Signals

Status-register alignment and grouping differ by generation; off-by-one loops can miss syncpoints. IRQ routing on HW8 depends on `num_syncpt_irqs`. Tests should cover all syncpoint ranges, multiple IRQ lines, 32-bit and 64-bit builds, threshold re-enable, and suspend/resume interrupt restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/intr_hw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/opcodes.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/opcodes.h

## Purpose

`opcodes.h` defines helpers for constructing host1x class register payloads and pushbuffer opcodes. It centralizes the command encoding consumed by channel submission, timeout recovery, and debug decoding.

## Important APIs, Types, And Functions

- Class payload helpers build wait, wait-base, load-base, increment-syncpoint, and indirect-register-access values using generated uclass field macros.
- Opcode helpers build SETCLASS, INCR, NONINCR, MASK, IMM, RESTART, GATHER, GATHER_NONINCR/INCR, SETSTREAMID, SETPAYLOAD, GATHER_W, ACQUIRE_MLOCK, and RELEASE_MLOCK words.
- `HOST1X_OPCODE_NOP` is encoded as `NONINCR(0, 0)`.

## Control Flow

All functions are pure inline encoders. Runtime flow is in `channel_hw.c`, which emits these words into the CDMA pushbuffer, and `debug_hw.c`, which decodes the same opcode nibbles.

## State And Persistence Behavior

The header stores no state. Encoded words become persistent pushbuffer contents until CDMA consumes or timeout recovery overwrites them.

## Dependencies And Integration Points

It depends on generated uclass field macros and Linux `BIT()`. It is included by each generation hardware umbrella header.

## Risks And Test Signals

The encodings are ABI-level hardware contracts. Wide gather and stream-ID opcodes are valid only on newer hardware; callers must gate them. Tests should compare emitted opcodes against known-good sequences for waits, gathers, stream-ID switching, MLOCK acquire/release, and restart padding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/opcodes.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/syncpt_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/syncpt_hw.c

## Purpose

`hw/syncpt_hw.c` implements generation-specialized syncpoint hardware operations. It saves/restores syncpoint and wait-base values, loads hardware min values into atomics, performs CPU increments, assigns syncpoints to channels on protected hardware, and enables syncpoint protection.

## Important APIs, Types, And Functions

- `syncpt_restore()` and `syncpt_restore_wait_base()` write cached min/wait-base values back to registers.
- `syncpt_read_wait_base()` reads wait-base state for generations that have it.
- `syncpt_load()` atomically updates `sp->min_val` from the live hardware register and checks against tracked max.
- `syncpt_cpu_incr()` writes CPU increment bits after validating non-client-managed idle state.
- `syncpt_assign_to_channel()` programs channel ownership on HW6+.
- `syncpt_enable_protection()` enables hypervisor syncpoint protection when available.

## Control Flow

Generic syncpoint code dispatches through `host1x_syncpt_ops`. On restore, all syncpoints are unassigned from channels before min values are restored and protection is enabled. Loading loops with `atomic_cmpxchg()` to avoid races updating `min_val`. CPU increments are rejected for idle, host-managed syncpoints to avoid unexpected max/min divergence.

## State And Persistence Behavior

Software state is `min_val`, `base_val`, and assignment/locked fields in `struct host1x_syncpt`. Hardware state includes syncpoint min registers, wait-base registers, CPU increment registers, channel assignment registers, and hypervisor protection enable.

## Dependencies And Integration Points

Depends on generated sync/VM/hypervisor register macros, `syncpt.c`, `dev.h`, and channel structures. It is included into each generation unit and varies by `HOST1X_HW`.

## Risks And Test Signals

Wait bases disappear on HW7+ in this implementation, so conditional no-ops must match hardware semantics. Protection requires hypervisor registers. Tests should cover CPU increments, min/max sanity errors, save/restore across runtime PM, channel assignment, protected syncpoint access, and old wait-base relative waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/syncpt_hw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.c

## Purpose

`intr.c` is the generic syncpoint fence interrupt manager. It maintains ordered fence lists per syncpoint, programs the next threshold into hardware, handles expired fences after IRQs, and requests syncpoint IRQ lines at probe.

## Important APIs, Types, And Functions

- `host1x_intr_add_fence_locked()` inserts a fence in threshold order and updates hardware state.
- `host1x_intr_remove_fence()` removes a queued fence from timeout/cancel paths and reprograms the next threshold.
- `host1x_intr_handle_interrupt()` loads the syncpoint value, signals all expired fences from the head of the list, and re-enables/disables hardware as needed.
- `host1x_intr_init()` initializes all fence lists, disables stale interrupts, allocates IRQ data, and requests each syncpoint IRQ.
- `host1x_intr_start()` initializes host sync hardware using the clock rate; `host1x_intr_stop()` disables all threshold interrupts.

## Control Flow

Fence insertion is done under the syncpoint fence-list spinlock already held by DMA fence code. The list is maintained ascending by threshold so IRQ handling can stop at the first unexpired fence. Hardware is programmed only for the first pending threshold per syncpoint. Probe-time IRQ setup supports multiple named syncpoint IRQs through `dev.c`.

## State And Persistence Behavior

Per-syncpoint fence lists persist in `struct host1x_syncpt`. Hardware threshold and interrupt-enable state mirrors the first pending fence. IRQ data is devm-managed for the host lifetime.

## Dependencies And Integration Points

Depends on `fence.c`, `syncpt.c`, hardware interrupt ops from `dev.h`, Linux IRQ APIs, and host clock for cycles-per-microsecond setup.

## Risks And Test Signals

Threshold ordering must handle 32-bit wrap comparisons consistently. Removing a fence from timeout races with IRQ signaling. Tests should cover multiple fences on one syncpoint, out-of-order threshold insertion, cancellation, timeout removal, suspend/resume interrupt reinitialization, and IRQ sharing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.h

## Purpose

`intr.h` declares the generic host1x syncpoint interrupt lifecycle and fence-list manipulation APIs.

## Important APIs, Types, And Functions

- `struct host1x_intr_irq_data`: per-IRQ host pointer plus status-register offset.
- Init/deinit/start/stop functions for syncpoint IRQ management.
- `host1x_intr_handle_interrupt()` dispatches one syncpoint's pending threshold.
- `host1x_intr_add_fence_locked()` and `host1x_intr_remove_fence()` connect fences to interrupt hardware.

## Control Flow

The header has no direct flow. Hardware ISRs call `host1x_intr_handle_interrupt()`; fence code queues and removes fences through the declared helpers.

## State And Persistence Behavior

No state is stored here. The declared structures are used for devm IRQ callback data.

## Dependencies And Integration Points

It is shared by `intr.c`, `intr_hw.c`, `fence.c`, `syncpt.h`, and `dev.h`.

## Risks And Test Signals

Function signatures are cross-file contracts between generic and hardware interrupt code. Build coverage plus runtime fence signaling validate them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.c

## Purpose

`job.c` implements host1x job allocation, reference counting, command descriptor construction, buffer pinning, relocation patching, optional command firewall validation/copying, unpin cleanup, and debug dumping.

## Important APIs, Types, And Functions

- `host1x_job_alloc()` lays out one allocation containing the job, relocs, unpin records, command descriptors, and DMA address arrays, with overflow checks.
- `host1x_job_get()` / `host1x_job_put()` manage references and release fences, syncpoints, and caller resources.
- `host1x_job_add_gather()` and `host1x_job_add_wait()` append command descriptors.
- `pin_job()` pins relocation targets and, when firewall is disabled, gather BOs; it creates IOMMU mappings for discontiguous gather SG tables where needed.
- `copy_gathers()` copies command buffers into trusted WC memory and validates opcodes/relocations when the firewall is enabled.
- `do_relocs()` patches relocation target addresses into gather command buffers or the firewall copy.
- `host1x_job_pin()` and `host1x_job_unpin()` are the public pin/unpin pair.

## Control Flow

Job allocation reserves enough trailing memory for the requested relocs/gathers/unpins. Pinning first pins relocation targets and validates access direction. If command firewall is enabled, gather buffers are copied into a host-owned DMA buffer, validated opcode by opcode, then relocated in the copy. Without firewall, gather BOs are pinned directly, mapped into contiguous IOVA if required, and relocated in place. On any pin error, previously pinned resources are unwound.

The firewall validator decodes host1x opcodes, tracks remaining words, class/register/count/mask state, and requires relocations for address registers reported by the client callback. Only supported opcodes are accepted; unknown or malformed streams return `-EINVAL`.

## State And Persistence Behavior

Jobs persist by kref while queued in CDMA and while users hold references. Pinning persists BO references, DMA mappings, IOVA allocations, copied gather buffers, relocated command words, `num_unpins`, and address arrays. Unpin releases mappings/BO refs and frees firewall gather copies.

## Dependencies And Integration Points

Depends on public host1x job structures, BO pin/mmap APIs, DMA/IOMMU/IOVA, channel/CDMA submit, syncpoints, fences, and client callbacks such as `is_addr_reg` and `is_valid_class`. DRM Tegra submit code populates these jobs.

## Risks And Edge Cases

Firewall validation accepts only a subset of opcodes and requires relocation ordering to match address-register writes. `copy_gathers()` must free its DMA copy on later unpin even after validation failure. IOMMU map failures and multi-chunk relocation targets are rejected. Relocation shifts are currently unsupported by validation. Tests should cover overflow allocation rejection, pin failure unwinds, firewall valid/invalid streams, duplicate gather BO handling, IOMMU gather mapping, and fence cleanup in `job_free()`.

## Test Signals

Submit tests with reloc read/write/bidirectional flags, firewall on/off, invalid class/register opcodes, address registers without relocations, gathers above 4 GiB, command-buffer copy allocation fallback, and timeout unpin paths provide strong coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.h

## Purpose

`job.h` defines internal host1x job command descriptors and unpin records used by job pinning and channel submission.

## Important APIs, Types, And Functions

- `struct host1x_job_gather`: gather word count, DMA base, BO pointer, byte offset, and duplicate-handled flag.
- `struct host1x_job_wait`: syncpoint ID, threshold, next class, and relative/absolute mode.
- `struct host1x_job_cmd`: tagged union of gather or wait command.
- `struct host1x_job_unpin_data`: BO mapping to release after completion.
- `host1x_job_dump()` emits debug details for a job.

## Control Flow

The header has no direct flow. `job.c` appends commands, `channel_hw.c` consumes them in order, and CDMA completion calls unpin.

## State And Persistence Behavior

These descriptors persist inside `struct host1x_job` while the job is pending. Submission mutates gather base/handled fields and wait thresholds may be interpreted relative to syncpoint max.

## Dependencies And Integration Points

Depends on DMA direction types and public host1x BO/job structures from includers. It is shared by job, CDMA, channel, and debug code.

## Risks And Test Signals

The `is_wait` tag must match the union member. Tests that mix waits and gathers, duplicate gather BOs, and relative waits validate the descriptor contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/job.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/mipi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/mipi.c

## Purpose

`mipi.c` implements the Tegra MIPI calibration provider/client helper API. It lets CSI/DSI consumers request a calibration device by devicetree phandle and call provider-supplied enable, disable, start, and finish operations.

## Important APIs, Types, And Functions

- `tegra_mipi_enable()`, `tegra_mipi_disable()`, `tegra_mipi_start_calibration()`, and `tegra_mipi_finish_calibration()` call optional provider ops and default to success.
- `tegra_mipi_request()` parses `nvidia,mipi-calibrate`, verifies it matches the singleton provider, obtains the provider platform device, stores ops and pad mask, and returns a handle.
- `tegra_mipi_free()` drops the platform-device reference and frees the handle.
- `devm_tegra_mipi_add_provider()` registers the singleton provider and removes it through a devm action.

## Control Flow

Provider registration stores a device node and ops if no provider exists. Consumers parse a phandle with `#nvidia,mipi-calibrate-cells`, require the parsed node to be the current provider, allocate a `tegra_mipi_device`, and hold a platform-device reference. Operation calls are thin optional callbacks into the provider.

## State And Persistence Behavior

The file stores one global provider `{np, ops}`. Each requested MIPI device stores the provider platform device, ops pointer, and pad selection. Provider state persists until the devm cleanup action clears it.

## Dependencies And Integration Points

Depends on OF phandle parsing, platform devices, and public `<linux/tegra-mipi-cal.h>`. It is registered from `dev.c` as a companion platform driver and used by display/camera drivers needing lane calibration.

## Risks And Test Signals

Only one provider is supported; a second returns `-EBUSY`. Provider matching is by node pointer, so DT must reference the exact provider. Tests should cover missing phandle, wrong provider, provider removal cleanup, request/free reference balance, and providers with partial operation tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/mipi.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.c

## Purpose

`syncpt.c` manages host1x syncpoint allocation, min/max shadow accounting, wait-base allocation, CPU increments, waits through DMA fences, save/restore across PM, and special VBLANK syncpoint reservations.

## Important APIs, Types, And Functions

- `host1x_syncpt_alloc()` / `host1x_syncpt_request()` allocate exclusive syncpoints, optional wait bases, names, and client-managed state.
- `host1x_syncpt_put()` releases syncpoints, resets max to current hardware value, frees wait bases and names, and clears lock/client flags.
- `host1x_syncpt_incr_max()`, `host1x_syncpt_read_max()`, `host1x_syncpt_read_min()`, and `host1x_syncpt_load()` maintain shadow max/min values.
- `host1x_syncpt_wait()` waits on a threshold using a host1x fence and supports polling/no-timeout behavior.
- `host1x_syncpt_save()` / `host1x_syncpt_restore()` preserve syncpoint state over runtime PM and re-enable protection.
- Lookup helpers get syncpoints by ID with or without a reference; vblank reservation release frees boot-reserved syncpoints 26/27 on older SoCs.

## Control Flow

Initialization allocates arrays for syncpoints and wait bases, assigns IDs, initializes the syncpoint mutex, reserves a NOP syncpoint, and optionally reserves VBLANK syncpoints. Allocation scans for the first zero kref, optionally claims a wait base, names the syncpoint, sets client-managed mode, and initializes the kref under `syncpt_mutex`. Waiting first loads current hardware state, returns immediately if expired, maps negative timeout to effectively infinite, creates a fence, waits, cancels on timeout, reloads the value, and verifies actual expiration.

## State And Persistence Behavior

Each syncpoint persists an ID, kref, atomic min/max shadows, base value, name, client-managed flag, host pointer, optional wait base, fence list, and locked flag. Hardware syncpoint values persist in registers and are restored from shadow during resume. VBLANK reservations use synthetic krefs until released by display code.

## Dependencies And Integration Points

Depends on hardware syncpoint ops, fence/interrupt code, tracepoints, DMA fences, and public host1x client APIs. Channel submission increments max and assigns syncpoints; timeout paths can lock failed syncpoints.

## Risks And Test Signals

32-bit wrap comparisons must remain consistent across wait, interrupt, and expiry checks. Host-managed syncpoints should be idle before suspend. Wait cancellation uses the fence timeout path. Tests should cover allocation exhaustion, wait bases, client-managed syncpoints, CPU increments, timeout waits, wraparound thresholds, vblank reservation release, runtime PM save/restore, and locked syncpoint rejection in CDMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.h

## Purpose

`syncpt.h` defines internal host1x syncpoint and wait-base structures plus helper APIs for allocation, state queries, save/restore, expiration checks, and max/min accounting.

## Important APIs, Types, And Functions

- `struct host1x_syncpt_base`: wait-base ID and allocation flag.
- `struct host1x_syncpt`: kref, ID, atomic min/max, wait-base value, name, client-managed flag, host pointer, optional base, fence list, and timeout lock flag.
- Inline helpers check max sanity, client-managed mode, idle state, valid ID, and set locked state.
- Prototypes expose init/deinit, counts, load, wait-base load, save/restore, expiration, and max increment.

## Control Flow

Most logic is inline predicates. `host1x_syncpt_is_expired()` and related APIs are implemented in `syncpt.c`/`syncpt_hw.c`.

## State And Persistence Behavior

The structures are allocated for the host lifetime. Atomic min/max and fence lists are mutated by submission, interrupts, waits, and PM paths.

## Dependencies And Integration Points

Includes public `<linux/host1x.h>`, atomic/kref primitives, `fence.h`, and `intr.h`. It is central to CDMA, channel, interrupts, debug, and client APIs.

## Risks And Test Signals

Idle and max sanity checks skip client-managed syncpoints by design. Build coverage, wraparound tests, and suspend/resume tests validate this header's invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.h -->
