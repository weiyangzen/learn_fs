# sources/distributed-fs/ceph-client/include/uapi/linux/stddef.h

## Purpose
Exports small compiler/layout helper macros usable by UAPI headers, especially for anonymous struct groups and flexible arrays embedded in unions.

## Important APIs, Types, and Constants
Defines `__always_inline` fallback, `__struct_group_tag`, `__struct_group(TAG, NAME, ATTRS, MEMBERS...)`, `__DECLARE_FLEX_ARRAY(TYPE, NAME)`, no-op counted-by annotations (`__counted_by`, `__counted_by_le`, `__counted_by_be`, `__counted_by_ptr`), and `__kernel_nonstring`.

## Control Flow, State, and Persistence
No runtime state. These macros influence C/C++ compilation and ABI layout. The C++ path for `__DECLARE_FLEX_ARRAY` uses a zero-length array because C++ does not treat empty structs like C.

## Dependencies and Integration Points
May include `<linux/compiler_types.h>` in kernel builds. Used by many UAPI structs, including headers with flexible arrays such as TCMU and packet editing.

## Risks and Test Signals
Risks are compiler incompatibility, C/C++ layout differences, and annotations not being available to userspace compilers. Test by compiling UAPI headers as C and C++, checking offsets for structs using `__struct_group`, and building with sparse/clang/gcc.
