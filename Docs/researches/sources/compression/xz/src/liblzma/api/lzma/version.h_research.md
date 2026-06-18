# sources/compression/xz/src/liblzma/api/lzma/version.h

Purpose: defines compile-time liblzma version macros and declares runtime version query functions.

Important APIs/types/functions: sets `LZMA_VERSION_MAJOR 5`, `MINOR 8`, `PATCH 3`, stable `LZMA_VERSION_STABILITY`, optional `LZMA_VERSION_COMMIT`, symbolic stability constants, numeric `LZMA_VERSION`, string construction macros, `LZMA_VERSION_STRING`, `lzma_version_number()`, and `lzma_version_string()`.

Control flow: compile-time macro arithmetic builds numeric and string versions. Runtime functions return the version of the linked liblzma, allowing applications to compare against compile-time headers.

State and persistence: no mutable state; version data is compile/link-time constant.

Dependencies/integration: included first by `lzma.h` so applications can gate feature usage. Windres can include parts of the header with `LZMA_H_INTERNAL_RC` to avoid function declarations.

Risks: headers and runtime library can differ; callers must use runtime functions when behavior depends on loaded library version. Commit suffix is string-only and not represented in the numeric macro.

Test signals: compile checks and any test/application displaying version. Packaging tests should verify version macros, pkg-config metadata, and runtime strings agree.
