# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt.h

### Purpose
`intel_gt.h` is the public GT core interface. It exposes GT lifecycle functions, fault/error helpers, PM and flushing helpers, iterator macros, workaround predicates, UC-to-GT conversion helpers, and small inline state queries used throughout i915 GT code.

### Important APIs, Types, And Functions
The header declares the core APIs implemented in `intel_gt.c`, including init/probe/remove/register/release routines, idle wait, fault clearing, GGTT flush helpers, info printing, coherent map selection, bind-context readiness, and asynchronous wedging. It also defines `IS_GFX_GT_IP_RANGE()`, `IS_MEDIA_GT_IP_RANGE()`, stepping predicates, `GT_TRACE()`, `gt_is_root()`, `NEEDS_FASTCOLOR_BLT_WABB()`, `for_each_gt()`, `for_each_engine()`, `for_each_engine_masked()`, `intel_gt_scratch_offset()`, `intel_gt_has_unrecoverable_error()`, and `intel_gt_is_wedged()`.

### Control Flow
Callers include this header to move between device, GT, UC, GuC, HuC, GSC, and engine objects and to iterate the active GT/engine arrays. Inline wedged checks read reset flags before request submission or hardware access. IP/stepping macros gate workarounds and feature paths at compile-time-checked version boundaries.

### State, Persistence, And Dependencies
The header stores no state, but its inlines depend on `struct intel_gt`, reset flags, engine masks, scratch VMA offsets, and platform version macros. It includes engine types, GT types, and reset declarations.

### Integration Points
Nearly all GT implementation files depend on this header for object conversion and iteration. Workaround, memory, PM, reset, UC, and engine code use the IP range macros to keep platform tests consistent.

### Risks
Incorrect platform predicates can apply or skip hardware workarounds broadly. Iterator macros assume `i915->gt[]` and `gt->engine[]` entries are stable under the caller's lifecycle context. The wedged helpers assert that unrecoverable init/fini wedge bits imply the main wedged bit.

### Test Signals
Compile coverage across graphics and media GT IP predicates, multi-GT iteration, mocked GTs, and code paths using `for_each_engine_masked()` are the main signals. Runtime signals include correct workaround selection on stepping-bound platforms and safe behavior after init/fini wedging.
