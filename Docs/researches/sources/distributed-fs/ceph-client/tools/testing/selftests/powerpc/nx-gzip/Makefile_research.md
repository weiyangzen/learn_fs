<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/Makefile

Purpose: Build definition for NX gzip accelerator selftests. It builds compression and decompression samples and runs them via a shell harness.

Important APIs and types: Defines `TEST_GEN_FILES := gzfht_test gunz_test`, `TEST_PROGS := nx-gzip-test.sh`, includes common lib/flags, and sets `CFLAGS = -O3 -m64 -I./include -I../include`.

Control flow: Both generated files link `gzip_vas.c` and `../utils.c`, giving them common VAS submission and file/sysfs helpers.

State and persistence: No runtime state beyond build outputs.

Dependencies and integration points: Depends on the local include directory, powerpc64 compiler support, and shared kselftest libraries.

Risks: If `gzip_vas.c` is not linked into both tools, hardware submission symbols are missing. The forced `-m64` reflects VAS/NX ABI expectations.

Test signals: Build success plus wrapper execution over random files validates the Makefile wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/Makefile -->
