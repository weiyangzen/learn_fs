# File Research: sources/cow-pools/bcachefs-tools/include/linux/compiler.h

This is the user-space compiler-compatibility layer for Linux kernel annotations and low-level access macros. It defines barriers, branch prediction, attributes, address-space annotations, sparse-style lock annotations, `__UNIQUE_ID`, `ACCESS_ONCE`, and many no-op kernel attributes.

It implements `READ_ONCE()` and `WRITE_ONCE()` using size-specialized volatile loads/stores with may-alias integer typedefs, falling back to memcpy surrounded by compiler barriers for aggregate sizes. `lockless_dereference()` combines `READ_ONCE()` with a dependency barrier.

The header also supplies cache flush no-ops, config detection for x86_64, constexpr/type helpers such as `__is_constexpr()`, `is_signed_type()`, `is_unsigned_type()`, `TYPEOF_UNQUAL`, `typeof_member()`, and `__cleanup()` for the cleanup helpers. It is a foundational include for many other compatibility headers.
