## sources/distributed-fs/beegfs/meta/source/pmq/pmq_base.hpp

Purpose: foundational PMQ utilities for attributes, assertions, alignment, byte slices, typed slices, and pointer wrappers. It keeps low-level helper code small and avoids heavier STL abstractions in hot PMQ headers.

Important APIs and types: `__pmq_cache_aligned`, `__pmq_profiled`, `__pmq_artificial_method`, `__pmq_artificial_func`, and `__pmq_formatter` centralize compiler attributes. `pmq_assert` wraps assertions and sleeps before failing in debug builds. `Untyped_Slice` and `Slice<T>` carry non-owning memory ranges with offset/sub-slice helpers. `copy_slice`, `copy_to_slice`, `copy_from_slice`, and `zero_out_slice` implement bounded memory copies. `Pointer<T>` wraps a non-null single-object pointer and intentionally does not expose array indexing.

Control flow: the file is header-only. Call sites construct slices around stack buffers, mmap regions, ring slots, chunk buffers, and serialized records, then use the helper functions to copy or zero exact ranges. Alignment helpers assert runtime alignment and feed `__builtin_assume_aligned` to the compiler.

State and persistence behavior: no persistent state is stored here, but these types are heavily used for PMQ persistence I/O. Incorrect slice sizes or alignment assumptions can directly affect `wal.dat`, `chunks.dat`, and `state.dat` writes.

Dependencies and integration points: uses libc, POSIX `sleep`, GCC attributes, and `__assert_fail`. The format diagnostic pragma makes PMQ format warnings hard errors for the translation units including this header.

Risks: compiler attributes and `#pragma GCC diagnostic error "-Wformat"` are GCC-oriented and may reduce portability. `Pointer<T>` asserts non-null but still has pointer semantics. Slice helpers rely on assertions for bounds, so release builds may not catch misuse before memory corruption.

Test signals: compile tests with and without `NDEBUG`/`PMQ_WITH_PROFILING`, format-string warning tests, alignment tests on mapped buffers, and fuzz-style slice subrange tests would protect this layer.
