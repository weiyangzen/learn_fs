# sources/distributed-fs/ceph-client/include/drm/drm_util.h

## Purpose
`drm_util.h` contains small DRM-internal utility macros and helpers that do not fit naturally elsewhere.

## Important APIs, types, and functions
`EXPORT_SYMBOL_FOR_TESTS_ONLY(x)` exports a symbol only when `CONFIG_DRM_EXPORT_FOR_TESTS` is enabled; otherwise it expands to nothing. `drm_can_sleep()` returns false when in atomic context, kgdb master context, or with IRQs disabled, and true otherwise.

## Control flow
DRM selftest-only functions use the export macro to avoid making test hooks visible in production builds. Existing legacy code can call `drm_can_sleep()` before choosing a sleeping versus non-sleeping path, though the header explicitly says not to use it in new code.

## State and persistence
There is no persistent state. `drm_can_sleep()` samples current task/interrupt/debugger context.

## Dependencies and integration points
The header depends on interrupt state, kgdb, preemption/atomic context checks, SMP, and generic utility macros. It integrates with DRM selftests and legacy paths that still branch on sleepability.

## Risks and test signals
Risks include relying on an imperfect atomic-context check, adding new callers despite deprecation, accidental production exports when test config is enabled, and behavior differences under kgdb. Test signals include CONFIG_DRM_EXPORT_FOR_TESTS builds, atomic/IRQ-off calls to `drm_can_sleep`, kgdb active checks, and audits that new code does not depend on this helper.
