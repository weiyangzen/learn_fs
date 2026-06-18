# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_user.c

## Purpose
This file builds the stable user-facing engine namespace from internal i915 engine objects. It sorts engines by UABI class and instance, assigns user-visible class/instance numbers and names, installs the lookup RB tree, derives scheduler capability bits, and reports which engine classes have default context isolation.

## Important APIs, Types, and Functions
`intel_engine_lookup_user()` searches `i915->uabi_engines` by class and instance. `intel_engine_add_user()` queues an engine onto `uabi_engines_llist` before final registration. `intel_engines_driver_register()` is the main registration pass: it drains the lockless list, sorts engines, filters incomplete GTs, assigns `uabi_class`, `uabi_instance`, final names, legacy indices, and RB-tree nodes, then validates debug mappings and sets scheduler caps. `intel_engines_has_context_isolation()` returns a bitmask of UABI classes with `default_state`. `intel_engine_class_repr()` maps internal classes to short names (`rcs`, `bcs`, `vcs`, `vecs`, `ccs`, `other`).

Internal helpers include `engine_cmp()`, `sort_engines()`, `set_scheduler_caps()`, `legacy_ring_idx()`, `add_legacy_ring()`, and `engine_rename()`. The `uabi_classes[]` table intentionally hides `OTHER_CLASS` from userspace by mapping it to `I915_NO_UABI_CLASS`.

## Control Flow
Engines are added during GT/engine initialization through `intel_engine_add_user()`. At driver registration, `intel_engines_driver_register()` drains the pending llist into a list, sorts it by UABI class then physical instance, and walks it once. Exposed engines are inserted into an RB tree in sorted order so later lookup is deterministic. Non-UABI engines are renamed but skipped for RB-tree exposure. The final pass computes global scheduler caps only for features available across all UABI engines.

## State and Persistence Behavior
The file mutates persistent driver state in `drm_i915_private`: `uabi_engines`, `engine_uabi_class_count`, and `caps.scheduler`. It also finalizes per-engine `uabi_class`, `uabi_instance`, `legacy_idx`, and `name`. Once registered, the mapping is expected to remain stable for the driver lifetime.

## Dependencies and Integration Points
It integrates with DRM UABI definitions (`I915_ENGINE_CLASS_*`, `I915_SCHEDULER_CAP_*`), execbuf legacy ring mapping, GuC submission capability reporting, GT unrecoverable-error state, and debug/selftest checks. Query ioctls and context engine selection depend on the RB tree created here.

## Risks
The UABI mapping must be deterministic; sorting or class-table mistakes can renumber engines and break userspace assumptions. Scheduler caps are deliberately intersection-style: if one engine lacks a feature, the global cap is disabled. Missing this can advertise unsupported scheduling behavior. Skipping engines from unrecoverable GTs prevents exposing half-initialized hardware, but also affects class counts and must match query expectations.

## Test Signals
Check `I915_QUERY_ENGINE_INFO` output for stable class/instance pairs, verify legacy execbuf rings map as expected, run debug selftests for UABI lookup/isolation, confirm scheduler caps match actual preemption/semaphore/stats behavior, and validate multi-GT failure paths do not expose incomplete engines.
