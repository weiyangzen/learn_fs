# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_ppgtt.h

## Purpose
Defines the gen6 PPGTT container, page-table index helpers, PDE iteration macros, and public PPGTT lifecycle functions.

## APIs And Control Flow
Defines `struct gen6_ppgtt`, `gen6_pte_index/count()`, `gen6_pde_index()`, `to_gen6_ppgtt()`, `gen6_for_each_pde()`, `gen6_for_all_pdes()`, and declarations for pin/unpin/enable/create. The macros iterate PDEs over rounded ranges or all entries and mutate their start/length variables.

## State, Dependencies, Integration, Risks, And Tests
The header stores no state but defines state owned by `gen6_ppgtt.c`. It depends on `intel_gtt.h` and a GEM ww-context forward declaration. Used by PPGTT implementation and engine/context code. Risks are side effects in macro arguments and incorrect container assumptions. Build-time checks, PPGTT tests, and live VM binding failures are signals.
