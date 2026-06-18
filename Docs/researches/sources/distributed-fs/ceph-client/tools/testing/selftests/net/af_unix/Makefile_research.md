# sources/distributed-fs/ceph-client/tools/testing/selftests/net/af_unix/Makefile

Purpose: Builds AF_UNIX-specific selftest binaries.

Important APIs/types/functions: Sets `top_srcdir`, includes `scripts/Makefile.compiler`, defines `cc-option`, adds `$(KHDR_INCLUDES) -Wall` and optional `-Wflex-array-member-not-at-end`, declares `TEST_GEN_PROGS` for `diag_uid`, `msg_oob`, `scm_inq`, `scm_pidfd`, `scm_rights`, `so_peek_off`, `unix_connect`, and `unix_connreset`, then includes `../../lib.mk`.

Control flow: Compiler feature detection adds a warning flag only when supported. Kselftest build rules compile each C file into a generated program.

State and persistence behavior: Build-only; generated binaries live under the kselftest output directory.

Dependencies and integration points: Requires kernel headers exposing newer AF_UNIX options such as `SO_PASSPIDFD`, `SO_PASSRIGHTS`, `SO_INQ`, `SO_PEEK_OFF`, and OOB support depending on individual tests.

Risks: Newer UAPI features can require up-to-date kernel headers; optional warning support avoids build failure on older compilers.

Test signals: Successful build produces all listed AF_UNIX test executables; runtime pass/fail is driven by each harness test.
