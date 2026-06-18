# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pm.h

## Purpose
This header declares the GEM power-management entry points used by the wider i915 driver during suspend, hibernation, idle work, and resume.

## Important APIs, Types, and Functions
It forward-declares `struct drm_i915_private` and `struct work_struct`, then exposes `i915_gem_resume`, `i915_gem_idle_work_handler`, `i915_gem_suspend`, `i915_gem_suspend_late`, `i915_gem_backup_suspend`, `i915_gem_freeze`, and `i915_gem_freeze_late`.

## Control Flow
There is no executable flow in the header. It allows driver PM code to call the staged GEM PM implementation in `i915_gem_pm.c`, with early suspend, late suspend, freeze, freeze-late, backup suspend, and resume split into explicit phases.

## State and Persistence Behavior
The header stores no state. The declared functions affect runtime PM wakerefs, GT state, object cache domains, shrink-list processing, and TTM LMEM backup objects in the implementation.

## Dependencies and Integration Points
It is included by driver suspend/resume paths and by GEM modules that need PM declarations. The `i915_gem_idle_work_handler` declaration is part of the broader GEM idle-work integration even though its implementation is elsewhere.

## Risks
The main risk is phase misuse: callers must invoke the right function at the right PM stage or local-memory preservation and cache coherency assumptions can fail. Header declarations must stay synchronized with implementation signatures.

## Test Signals
Build coverage catches signature drift. Runtime PM, system suspend, hibernation, and module unload paths validate that each declared hook remains wired into the platform lifecycle.
