<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/Makefile

Purpose: Build definition for the PAPR energy/frequency attributes selftest.

Important APIs and types: Defines `TEST_GEN_PROGS := attr_test`, includes kselftest libs and powerpc flags, and links with `../harness.c` plus `../utils.c`.

Control flow: Normal kselftest build emits the single `attr_test` binary.

State and persistence: No runtime state is defined here.

Dependencies and integration points: Depends on the parent selftest framework and `attr_test.c`.

Risks: If the target is omitted, PAPR attribute coverage disappears from test enumeration.

Test signals: Build and run discovery of `attr_test` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/papr_attributes/Makefile -->
