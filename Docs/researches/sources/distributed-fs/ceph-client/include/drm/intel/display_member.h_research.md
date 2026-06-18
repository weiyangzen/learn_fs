# sources/distributed-fs/ceph-client/include/drm/intel/display_member.h

Purpose: provides a compile-time contract that Intel parent driver structs place their `struct drm_device` member and `struct intel_display *` member at matching relative offsets. This lets shared display code recover the display pointer without needing concrete i915 or xe private struct definitions.

Important APIs/types/functions: `struct __intel_generic_device` is the reference layout with `drm` followed by `display`. `INTEL_DISPLAY_MEMBER_STATIC_ASSERT(type, drm_member, display_member)` compares the reference offset delta with a target struct's delta using `offsetof`, `static_assert`, and `__stringify`.

Control flow: no runtime control flow. The macro runs during compilation of drivers that include it and fails the build when the layout contract is violated.

State and persistence: no runtime state. The only persisted behavior is a build-time ABI-like invariant between Intel display and parent device structures.

Dependencies and integration: depends on `linux/build_bug.h`, `stddef.h`, `stringify.h`, and DRM device definitions. Used by Intel i915/xe display integration where the same display library must operate with multiple parent devices.

Risks and test signals: the main risk is a parent struct refactor that moves only one member and silently breaks pointer derivation if the assertion is absent. Build coverage for both i915 and xe private structs is the key test signal.
