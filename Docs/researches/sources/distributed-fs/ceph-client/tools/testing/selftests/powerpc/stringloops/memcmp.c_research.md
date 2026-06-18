# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/memcmp.c

Purpose: randomized and boundary-sensitive harness for imported powerpc `test_memcmp()` assembly implementations.

Important APIs/types/functions: `enter_vmx_ops()`/`exit_vmx_ops()` track VMX critical-section pairing; `test_one()` compares libc `memcmp()` with `test_memcmp()` for many offsets/sizes; `testcase()` builds protected mappings and randomized data.

Control flow: the test maps four pages, places two buffers at page ends, unmaps following pages to catch overreads, then runs small and large randomized cases with single-byte and multi-byte differences. It verifies only sign equivalence, matching C `memcmp()` contract, and checks VMX enter/exit count returns to zero.

State and persistence behavior: `vmx_count` is global instrumentation state. Mappings are per-process and not fully unmapped at the end, acceptable for one-shot tests.

Dependencies and integration points: links to either `memcmp_64.S` or `memcmp_32.S`, plus `utils.c`; 64-bit path skips if Power ISA 2.07 vector compare support is absent.

Risks and test signals: randomness is time-seeded, so failures may be hard to reproduce exactly. Protected page placement is the main signal for illegal overread.
