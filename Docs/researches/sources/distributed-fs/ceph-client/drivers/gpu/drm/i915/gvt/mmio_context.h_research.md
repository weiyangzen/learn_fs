# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio_context.h

## Purpose
`mmio_context.h` declares the render/engine MMIO context-switch interface for GVT.

## Important APIs, Types, And Functions
It forward-declares i915/GVT request, context, engine, device, and vGPU types. It declares `intel_gvt_switch_mmio`, `intel_gvt_init_engine_mmio_context`, `is_inhibit_context`, and `intel_vgpu_restore_inhibit_context`.

## Control Flow
No executable flow exists here. Callers initialize engine MMIO context once, switch MMIO on scheduling transitions, check inhibit status, and emit restore commands when required.

## State And Persistence
The declared functions operate on `gvt->engine_mmio_list`, `vgpu->mmio.vreg`, i915 context state, and request ring buffers; the header owns no state.

## Dependencies And Integration Points
It includes `linux/types.h` and is consumed by scheduler, submission, and initialization code.

## Risks
Callers must pass valid engine/context/request objects and respect scheduler/engine locking expectations or risk MMIO state leakage and command-stream corruption.

## Test Signals
Compile/link coverage, correct scheduling transitions, inhibit-context workloads with expected registers, and host transitions restoring non-vGPU values.
