# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_user.h

## Purpose
This header declares the engine UABI registration and lookup interface used by i915 driver setup, query paths, and context isolation reporting.

## Important APIs, Types, and Functions
The header forward-declares `struct drm_i915_private` and `struct intel_engine_cs`, then exports `intel_engine_lookup_user()`, `intel_engines_has_context_isolation()`, `intel_engine_add_user()`, `intel_engines_driver_register()`, and `intel_engine_class_repr()`.

## Control Flow
There is no internal control flow. Engine initialization code calls `intel_engine_add_user()` before final registration. Driver registration calls `intel_engines_driver_register()`. Later UABI/query code uses `intel_engine_lookup_user()` and `intel_engine_class_repr()`.

## State and Persistence Behavior
The header owns no state. Its functions manage persistent UABI engine state in `drm_i915_private` and per-engine UABI fields implemented in `intel_engine_user.c`.

## Dependencies and Integration Points
It is included by engine setup and userspace-facing engine query/registration code. It keeps the UABI mapping implementation private while exposing the minimal operations needed by the rest of i915.

## Risks
Prototype drift between this header and `intel_engine_user.c` would break engine registration or query builds. Because these calls define the user-visible engine namespace, any signature or semantic change must be coordinated with the UABI consumers.

## Test Signals
Build coverage is the main signal. Runtime signals are successful engine registration, working user-engine lookup, and correct scheduler/context-isolation reporting.
