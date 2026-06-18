# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_params.h

Purpose: declares the display module-parameter schema and the public helpers used to dump, copy, and free i915 display parameters. It is the canonical list of display-specific runtime and boot-time tuning knobs.

Important APIs, types, and functions: `INTEL_DISPLAY_PARAMS_FOR_EACH(param)` enumerates every parameter as `(type, name, default, debugfs_mode)`. `struct intel_display_params` is generated from that macro, ensuring field layout matches the parameter schema. Exported prototypes are `intel_display_params_dump()`, `intel_display_params_copy()`, and `intel_display_params_free()`.

Control flow: including code supplies a function-like macro to `INTEL_DISPLAY_PARAMS_FOR_EACH()` to generate declarations, struct members, initialization, dump loops, debugfs entries, or cleanup loops. The schema includes both boot-only/read-mostly policy fields and debugfs-writable feature toggles via the `mode` argument.

State and persistence: this header defines the in-memory shape of per-display parameter state. It does not store state directly, but every field becomes part of the driver's display configuration for the life of a display instance. Pointer fields require copy/free handling in the implementation.

Dependencies and integration points: depends on Linux integer/bool types and forward-declares `struct drm_printer`. It is included by parameter implementation code and by display initialization paths that need `display->params`. Integration is broad because fields influence firmware loading, display power management, connector probing, panel policy, display compression, and link features.

Risks: the macro list is order- and type-sensitive. A new type must be supported by all macro users in `intel_display_params.c` and any debugfs code. Debugfs mode values must be chosen carefully because some parameters are not safe to mutate after hardware initialization. Default changes can alter platform power behavior before tests reach modeset paths.

Test signals: compile errors from macro users reveal unsupported schema changes. Runtime validation comes from module parameter defaults, debugfs file modes, parameter dump output, and targeted tests that boot with non-default i915 display parameters.
