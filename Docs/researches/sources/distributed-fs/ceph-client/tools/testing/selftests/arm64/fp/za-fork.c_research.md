<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork.c

Purpose: C wrapper for the ZA fork preservation test.

Important APIs and functions: declares assembly `fork_test` and `verify_fork`. `fork_test_c` forks, has the child and parent call `verify_fork`, waits for child exit, and combines results. `main` sets a one-test plan and checks `/proc/sys/abi/sme_default_vector_length` as a nolibc-compatible SME availability proxy.

Control flow: if SME proxy file opens, run `fork_test`; otherwise skip. Child exits 1 on successful verification and 0 on failure so the parent can combine `WEXITSTATUS(child_status) && parent_result`.

State and persistence: no file writes; opens procfs read-only. Depends on ZA state prepared by assembly.

Dependencies and integration: paired with `za-fork-asm.S`, `kselftest.h`, nolibc-compatible headers, and Linux wait/fork APIs.

Risks: using procfs default VL as support detection can misclassify unusual systems. Child exit convention is inverted relative to normal pass/fail and must remain understood by parent code.

Test signals: one TAP result named `fork_test`; diagnostic messages identify parent/child invalid ZA state or wait failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-fork.c -->
