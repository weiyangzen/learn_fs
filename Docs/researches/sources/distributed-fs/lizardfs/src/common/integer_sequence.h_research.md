# sources/distributed-fs/lizardfs/src/common/integer_sequence.h

Purpose: backports `std::integer_sequence`, `std::index_sequence`, and make-sequence utilities for older C++ standards.

Important APIs/types/functions: `integer_sequence<T, Is...>`, `merge_integer_sequence`, recursive `make_integer_sequence<T,N>`, `index_sequence<Is...>`, `merge_index_sequence`, and recursive `make_index_sequence<N>`.

Control flow: recursive templates split `N` into halves and merge sequences while offsetting the right side by the left length.

State and persistence: compile-time types only.

Dependencies and integration: depends on `<cstddef>`. Used by `galois_coeff.h` and tuple hashing.

Risks: deep template recursion is logarithmic but still compile-time work. This custom implementation can conflict semantically if mixed with `std::integer_sequence` APIs expecting exact standard names in namespace `std`.

Test signals: `integer_sequence_unittest.cc` converts generated sequences into vectors and compares with `iota` results.
