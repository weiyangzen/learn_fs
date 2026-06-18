# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen7_renderclear.h

## Purpose
Declares the gen7 render GPR clear-batch setup helper.

## APIs And Control Flow
Forward-declares `struct intel_engine_cs` and `struct i915_vma`, and declares `gen7_setup_clear_gpr_bb()`. The function contract is two-mode: null VMA returns required size; non-null VMA fills an allocated batch object.

## State, Dependencies, Integration, Risks, And Tests
The header stores no state and has only forward-declaration dependencies. It is included by render engine setup code. Risk is callers ignoring the size-query contract and providing too-small VMAs. Build coverage and render-clear execution tests validate it.
