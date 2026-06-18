<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/Makefile

Purpose: build rules for arm64 Memory Tagging Extension selftests.

Important definitions: sets `CFLAGS += -std=gnu99 -I. -pthread`, `LDFLAGS += -pthread`, discovers all `.c` files except `mte_common_util.c` as programs, and checks compiler support for `-march=armv8.5-a+memtag` unless using LLVM.

Control flow: if compiler supports MTE, assigns `TEST_GEN_PROGS := $(PROGS)` and adds dependency on `mte_common_util.c mte_helper.S`; otherwise emits warnings and builds no MTE tests. Includes `../../lib.mk`.

State and persistence: build artifacts only.

Dependencies and integration: relies on GCC/Clang MTE support, pthread, shared MTE utility C/assembly files, and kselftest lib.mk.

Risks: compiler probe uses shell syntax embedded in make; nonstandard compilers may be misdetected. Excluding only `mte_common_util.c` means any helper `.c` added later could accidentally become a test binary.

Test signals: successful build produces one binary per test `.c` when support is detected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/Makefile -->
