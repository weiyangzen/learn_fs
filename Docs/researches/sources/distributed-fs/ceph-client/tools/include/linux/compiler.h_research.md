# sources/distributed-fs/ceph-client/tools/include/linux/compiler.h

## Purpose

This is the main tools compiler abstraction header. It provides compile-time assertions, barriers, attributes, access annotations, branch prediction, type helpers, and `READ_ONCE`/`WRITE_ONCE`.

## APIs, State, and Dependencies

It includes `compiler_types.h`, defines `compiletime_assert`, `barrier`, inline and attribute fallbacks, `__same_type`, constexpr helpers, annotation stubs such as `__user`, `__rcu`, `__iomem`, `likely`, `unlikely`, may-alias integer typedefs, and size-specialized `__read_once_size`/`__write_once_size`. Public `READ_ONCE` and `WRITE_ONCE` use alias-safe volatile loads/stores for 1, 2, 4, and 8 bytes and memcpy with barriers for larger objects. It also defines token-paste helpers and build-bug machinery.

## Risks and Test Signals

This header affects almost every copied kernel helper. Incorrect `READ_ONCE`/`WRITE_ONCE` semantics can break lock-free code, while attribute fallbacks can hide missing compiler support. Tests should compile a broad tools set under GCC and Clang, exercise once-access macros for scalar and aggregate types, and validate compile-time assertions.
