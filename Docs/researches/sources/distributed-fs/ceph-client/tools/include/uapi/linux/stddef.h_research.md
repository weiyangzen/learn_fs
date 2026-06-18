<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/stddef.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/stddef.h

Purpose: this compatibility header provides small UAPI helper macros for inline behavior, grouped structs, flexible arrays in unions, counted-by annotations, and nonstring markers.

Important APIs/types: `__always_inline` defaults to `__inline__` if absent. `__struct_group()` creates anonymous and named mirrored struct members inside a union so callers can address a group by name while preserving direct member access. `__DECLARE_FLEX_ARRAY()` handles C vs C++ flexible-array constraints. `__counted_by*` macros are annotation placeholders when compiler support is absent. `__kernel_nonstring` marks non-NUL string-like buffers.

Control flow: no runtime flow; these macros affect C/C++ declarations at compile time.

State and persistence: no state. ABI risk is layout: `__struct_group` and flexible-array macros must preserve intended struct size and member offsets.

Dependencies/integration: broadly used by UAPI structs that need flexible arrays or grouped layout without depending on newer compiler extensions. It is important for generated bindings and C++ consumers.

Risks and test signals: test with C and C++ compilation, `sizeof`, `offsetof`, and flexible-array placement in unions. Watch spelling/parameter compatibility because these macros are consumed by many headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/stddef.h -->
