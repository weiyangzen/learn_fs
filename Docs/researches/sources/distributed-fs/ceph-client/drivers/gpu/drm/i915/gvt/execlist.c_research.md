# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/execlist.c

## Purpose
`execlist.c` emulates Intel execlist submission state for a vGPU. It converts guest ELSP descriptor writes into GVT workload objects, updates virtual execlist status and context status buffers, and synthesizes context-switch interrupts so the guest driver sees the expected scheduling lifecycle.

## Important APIs And Functions
The central exported API is `intel_vgpu_submit_execlist(vgpu, engine)`. The file also exports `intel_vgpu_execlist_submission_ops`, whose `init`, `reset`, and `clean` callbacks wire this implementation into `struct intel_vgpu_submission_ops`. Internal control is split between `emulate_execlist_schedule_in()`, `emulate_execlist_ctx_schedule_out()`, `emulate_execlist_status()`, `emulate_csb_update()`, `submit_context()`, `prepare_execlist_workload()`, and `complete_execlist_workload()`.

## Control Flow
`intel_vgpu_submit_execlist()` reads two context descriptors from `execlist->elsp_dwords`, rejects invalid descriptor zero or non-privileged GGTT submissions, and creates one workload for each valid descriptor. The first descriptor in a bundle carries `emulate_schedule_in=true`, causing `prepare_execlist_workload()` to update virtual execlist state before workload execution.

Schedule-in picks the next virtual slot from the current status register. If no slot is running, the new slot becomes running and an idle-to-active CSB event is emitted. If an existing context can be lite-restored/preempted by the new descriptor, the pending slot becomes running and a lite-restore/preempted CSB event is emitted. Otherwise the new slot is stored as pending and the status queue-full bit is updated.

On workload completion, `complete_execlist_workload()` skips schedule-out if the workload failed, its engine is resetting, or the next queued workload has the same context. Otherwise `emulate_execlist_ctx_schedule_out()` emits element-switch or active-to-idle/context-complete events and promotes pending work when needed.

## State And Persistence
State is per vGPU and per engine in `vgpu->submission.execlist[]`: two virtual slots, running slot, pending slot, running context pointer, and cached ELSP dwords. The code updates virtual MMIO status registers and, when the guest HW status page can be translated through GGTT, mirrors CSB data and write pointer into guest memory with `intel_gvt_write_gpa()`. No state survives vGPU destruction except normal guest-visible memory effects.

## Dependencies And Integration Points
The file depends on GVT workload creation/queueing, engine iteration and IDs from i915, GTT translation for HWSP writes, virtual event injection for context-switch interrupts, and descriptor/status layouts from `execlist.h`. It integrates with scheduler code through workload `prepare` and `complete` callbacks.

## Risks And Edge Cases
The slot model is a simplified hardware emulation and is sensitive to descriptor equality (`context_id` and `lrca`) and running-context pointer validity. Bad ELSP descriptors return `-EINVAL`, queue-full state rejects new slots, and missing HWSP translation silently limits updates to MMIO CSB state. Incorrect pending/running transitions can deadlock guest scheduling or generate wrong interrupt ordering.

## Test Signals
Signals include guest GPU workloads completing without hangs, context-switch interrupts arriving, CSB write pointer advancing modulo the emulated buffer, lite-restore paths when identical contexts are submitted, pending slot behavior under two-descriptor submissions, and clean reset of execlist state on engine reset.
