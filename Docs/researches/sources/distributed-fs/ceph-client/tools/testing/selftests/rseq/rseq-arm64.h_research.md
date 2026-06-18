# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm64.h

Purpose: `rseq-arm64.h` defines the AArch64 rseq architecture layer: trap signature, memory barriers, acquire/release primitives, descriptor-section encoding, and assembly operation macros.

Important APIs, types, and functions: it defines `RSEQ_SIG_CODE`, endian-adjusted `RSEQ_SIG_DATA`, `RSEQ_SIG`, `rseq_smp_*` barriers, typed `rseq_smp_load_acquire()` and `rseq_smp_store_release()`, scratch registers `x15`, `w15`, `x14`, table/exit/abort macros, compare/store/load/add macros, and byte-copy helpers.

Control flow: the header sets up reusable operation snippets, then includes `rseq-arm64-bits.h` for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed helpers. The generated functions are then selected by the generic wrappers in `rseq.h`.

State and persistence: state is not stored in this header directly, but its macros define how generated helpers publish `struct rseq_abi_cs` records into ELF sections and how they store the active critical-section pointer into the TLS ABI area.

Dependencies and integration points: selected by `rseq.h` for `__AARCH64EL__`. It depends on AArch64 barrier and load-acquire/store-release instructions. It integrates with `param_test.c` and any other selftest including `rseq.h` on AArch64.

Risks and test signals: risks include endian-specific signature representation, missing clobbers for scratch registers, and unsupported object sizes in acquire/release helpers. Passing selftests on AArch64, especially `-M` release-mode buffer/memcpy runs, are the main validation signals.
