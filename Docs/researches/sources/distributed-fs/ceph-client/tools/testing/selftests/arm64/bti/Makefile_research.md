# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/Makefile

Purpose: builds freestanding arm64 Branch Target Identification test binaries with and without BTI properties.

Important APIs/types/functions: `TEST_GEN_PROGS := btitest nobtitest`; `CFLAGS_BTI` uses `-mbranch-protection=standard -DBTI=1`; `CFLAGS_NOBTI` uses `-mbranch-protection=none -DBTI=0`; object lists include test, signal, start, syscall, system, stubs, and trampoline variants; links static `-nostdlib` binaries; includes `../../lib.mk`.

Control flow: pattern rules compile every C/S file twice, once BTI and once non-BTI, then link corresponding binaries.

State and persistence: build outputs only.

Dependencies/integration: arm64 toolchain with branch-protection support and local freestanding runtime files.

Risks and test signals: dynamic loader BTI support is intentionally avoided. The `nobtitest` link still uses `$(CFLAGS_BTI)` in the command, but its objects are compiled non-BTI; note/property behavior should be checked if failures appear.
