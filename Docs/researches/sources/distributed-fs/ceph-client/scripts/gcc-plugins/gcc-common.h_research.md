# sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-common.h

Purpose: Central compatibility and convenience header for Linux GCC plugins across GCC internal API versions.

Important APIs/types: Includes a broad set of GCC internal headers. Defines visibility/unused macros, declaration/type name helpers, `build_const_char_string()`, `add_type_attr()`, `PASS_INFO`, compatibility no-op macros for old APIs, cgraph/varpool wrappers, gimple type aliases and casts, IPA reference wrappers, RTL helper aliases, and version-specific verification macro mappings.

Control flow: Plugin source includes this header before using GCC internals. Helpers adapt to the GCC version selected by `BUILDING_GCC_VERSION` and expose stable names used by plugin implementations.

State/persistence: No runtime state, but functions mutate GCC tree attributes, symbol tables, and pass structures in the current compiler process.

Dependencies/integration: Requires GCC plugin development headers and kernel-provided compiler-version definitions. Used by latent entropy, randstruct, stackleak, and generated pass headers.

Risks: GCC internal APIs are unstable; this header must track version changes closely. `add_type_attr()` mutates canonical/main variants and can affect type identity. Some macros intentionally stub old API functions, which can hide semantic differences.

Test signals: Compile all plugins across supported GCC versions, exercise type attribute propagation, cgraph edge rebuilds, IPA wrappers, and GIMPLE casts under checking-enabled GCC.
