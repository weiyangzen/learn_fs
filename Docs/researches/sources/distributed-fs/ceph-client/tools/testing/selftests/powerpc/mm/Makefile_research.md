<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/Makefile

Purpose: Build and run definition for powerpc memory-management selftests. It enumerates executable tests for huge pages, permissions, pkeys, stack growth, bad accesses, and TLBIE stress.

Important APIs and types: Defines `TEST_GEN_PROGS`, `TEST_PROGS`, `TEST_GEN_PROGS_EXTENDED`, and `TEST_GEN_FILES`. Adds 64-bit CFLAGS to tests needing high addresses or powerpc64 ABI, pthread libraries for `tlbie_test`/`pkey_siginfo`, and a generated `tempfile`.

Control flow: Default `noarg` recurses to the parent. Normal builds produce the listed binaries plus `stress_code_patching.sh`; `tlbie_test` is extended rather than a default generated program.

State and persistence: No runtime persistence except generated build files and `tempfile` under `OUTPUT`.

Dependencies and integration points: Depends on `../../lib.mk`, `../flags.mk`, shared `harness.c`, `utils.c`, and `../pmu/lib.c` for stack signal plumbing.

Risks: Misclassified targets or missing `-m64` flags would silently reduce high-address test coverage. The generated tempfile is required by `subpage_prot` file-backed coverage.

Test signals: Signals are successful compilation, test enumeration by kselftest, and the ability to run both default and extended MM tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/Makefile -->
