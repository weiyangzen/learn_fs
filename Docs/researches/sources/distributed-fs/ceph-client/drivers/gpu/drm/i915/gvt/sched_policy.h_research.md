# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/sched_policy.h

## Purpose
`sched_policy.h` declares the scheduling-policy abstraction and public scheduler control functions for Intel GVT-g.

## Important APIs, Types, And Functions
`struct intel_gvt_sched_policy_ops` defines callbacks for global init/clean, per-vGPU init/clean, and per-vGPU start/stop scheduling. Public functions include `intel_gvt_schedule`, global/per-vGPU init and cleanup, start/stop, and `intel_gvt_kick_schedule`.

## Control Flow
No executable flow exists here. Normal sequence is global init, per-vGPU init, start on guest submission enablement, kick on events, stop during teardown, and clean during device removal.

## State And Persistence
The API manipulates `gvt->scheduler.sched_ops`, `gvt->scheduler.sched_data`, and `vgpu->sched_data`; the header owns no storage.

## Dependencies And Integration Points
It forward-declares GVT types and is included by scheduling, KVMGT init/cleanup, MMIO handlers, and workload scheduler code.

## Risks
The ops table must be installed before per-vGPU calls and remain valid until cleanup. New policies must honor existing `gvt->sched_lock` expectations.

## Test Signals
Compile coverage plus runtime vGPU create/start/kick/stop/destroy flows. Any replacement policy should pass workload dispatch and teardown tests.
