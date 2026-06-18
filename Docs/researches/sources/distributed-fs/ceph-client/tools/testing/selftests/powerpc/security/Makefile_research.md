# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/Makefile

Purpose: builds the powerpc security mitigation selftests for RFI, entry, uaccess, and Spectre v2 behavior.

Important APIs/types/functions: declares `TEST_GEN_PROGS := rfi_flush entry_flush uaccess_flush spectre_v2` and `TEST_PROGS := mitigation-patching.sh`, pulls in `../../lib.mk` and `../flags.mk`, and adds `$(KHDR_INCLUDES)`.

Control flow: build rules link common `../harness.c` and `../utils.c`; `spectre_v2` is forced to `-m64` and links `../pmu/event.c` plus `branch_loops.S`; the flush tests link `flush_utils.c`.

State and persistence behavior: no runtime state. Generated binaries are under `$(OUTPUT)` per kselftest conventions.

Dependencies and integration points: integrates with kselftest make infrastructure and powerpc PMU/security helpers.

Risks and test signals: missing PMU headers, 64-bit compiler support, or assembly support breaks build before runtime. The shell mitigation stress test is included as a script rather than a generated binary.
