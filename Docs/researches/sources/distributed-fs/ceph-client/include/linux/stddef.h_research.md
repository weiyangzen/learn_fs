<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stddef.h -->
# sources/distributed-fs/ceph-client/include/linux/stddef.h

Purpose: Defines kernel equivalents of common Cstddef constructs and layout helper macros for safer structure introspection and flexible-array patterns.

Important APIs/types/functions: `NULL`, anonymous enum `false/true`, `offsetof()`, `sizeof_field()`, `offsetofend()`, `struct_group()`, `struct_group_attr()`, `struct_group_tagged()`, `DECLARE_FLEX_ARRAY()`, `__TRAILING_OVERLAP()`, and `TRAILING_OVERLAP()`.

Control flow: Pure macro definitions. Struct group macros create mirrored anonymous/named substructures with identical layouts; trailing overlap creates a union allowing a flexible array member to overlap explicitly declared trailing fields.

State and persistence behavior: No runtime state, but macros define compile-time structure layout and affect ABI/layout of containing structs.

Dependencies: UAPI `linux/stddef.h` for lower-level helper macros such as `__struct_group` and `__DECLARE_FLEX_ARRAY`, and compiler `__builtin_offsetof`.

Integration points: Kernel structures needing layout-safe grouped fields, flexible arrays in unions, and compile-time size/offset checks.

Risks: Layout macros affect ABI and must be used carefully in UAPI or packed structures. `TRAILING_OVERLAP` must match the intended flexible-array offset exactly.

Test signals: Compile-time layout assertions, `offsetof`/`sizeof_field` tests, flexible-array warning tests, and structure group ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stddef.h -->
