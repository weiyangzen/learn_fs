# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_irq.c

## Purpose

`vc4_irq.c` handles V3D engine interrupts for original GEN_4 VC4. It acknowledges binning flush completion, render completion, and binner out-of-memory events; moves jobs between bin/render/done queues; signals fences and wait queues; schedules overflow memory allocation work; and provides install/uninstall/reset helpers used by the V3D platform driver.

## Important APIs, Types, and Functions

- `vc4_overflow_mem_work()` allocates or rotates binner overflow memory and re-enables the OUTOMEM interrupt.
- `vc4_irq_finish_bin_job()` moves the first bin job to the render queue and may submit the next bin job if perfmon compatibility allows.
- `vc4_cancel_bin_job()` restarts binning after reset by stopping perfmon if needed, rotating the current bin job, and submitting the next one.
- `vc4_irq_finish_render_job()` moves the first render job to the done list, updates sequence/fence/wait state, controls perfmon stop/restart behavior, schedules job cleanup, and starts next render or bin work.
- `vc4_irq()` is the IRQ handler for `V3D_INT_OUTOMEM`, `V3D_INT_FLDONE`, and `V3D_INT_FRDONE`.
- Public lifecycle functions are `vc4_irq_enable()`, `vc4_irq_disable()`, `vc4_irq_install()`, `vc4_irq_uninstall()`, and `vc4_irq_reset()`.

## Control Flow

Install prepares wait queues/work items, clears stale interrupts, requests the IRQ, and enables FLDONE/FRDONE. The main IRQ handler reads and acknowledges `V3D_INTCTL`, disables OUTOMEM and schedules work if the binner needs more memory, handles bin completion under `job_lock`, and handles render completion under `job_lock`.

Overflow work runs outside IRQ context under `bin_bo_lock`, gets a free overflow slot, accounts for any previous overflow slot against the current bin job or last render job, writes `V3D_BPOA/BPOS`, clears OUTOMEM, and re-enables OUTOMEM. Render completion increments `finished_seqno`, moves the job to `job_done_list`, manages perfmon lifetimes, signals the DMA fence, wakes job waiters, and schedules deferred job cleanup. Reset acknowledges stale IRQs, enables all driver IRQs, cancels/requeues the current bin job, and finishes a render job if present.

## State and Persistence

State lives in `struct vc4_dev`: IRQ number, V3D presence, job lists, `job_lock`, `bin_bo_lock`, `bin_bo`, overflow allocation bitmaps, `finished_seqno`, wait queue, work items, and perfmon/job/fence references. Interrupt registers persist in V3D hardware until acknowledged or disabled. No disk persistence exists.

## Dependencies and Integration Points

The file depends on V3D register macros, VC4 job scheduler helpers (`vc4_first_bin_job()`, `vc4_move_job_to_render()`, `vc4_submit_next_*()`, etc.), BO allocation helpers, perfmon helpers, DMA fences, wait queues, workqueues, and tracepoints. It is invoked from `vc4_v3d.c` during V3D bind/remove/runtime power transitions and reset.

## Risks and Edge Cases

- Only GEN_4 is supported; every public path warns and returns for later generations.
- OUTOMEM stays asserted until memory is supplied, so the handler disables it and relies on workqueue completion to avoid interrupt storms.
- Overflow memory ownership is tied to in-flight bin/render jobs; wrong slot accounting can leak or prematurely reuse binner memory.
- Perfmon compatibility gates bin/render job submission; mishandling can collect wrong counters or stall queues.
- Fence signaling and job list moves happen under `job_lock`; missing locking would race userspace waits and cleanup work.
- `IRQ_NOTCONNECTED` is reported as `-ENOTCONN`, so probe paths must tolerate platforms without a connected interrupt.

## Test Signals

Signals include V3D job submission tests that observe bin/render completion, DMA fence signaling, wait queue wakeups, overflow-memory pressure scenarios, GPU reset paths invoking `vc4_irq_reset()`, runtime suspend/resume disabling/enabling IRQs, tracepoints for BCL/RCL end IRQs, and lockdep around `job_lock`/`bin_bo_lock`.
