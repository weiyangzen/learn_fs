<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcspushm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcspushm.S

Purpose: standalone assembly smoke test that enables GCS push permission and executes GCSPUSHM/GCSPOPM.

Important APIs and symbols: `_start` uses raw `prctl(PR_SET_SHADOW_STACK_STATUS, ENABLE|PUSH)`, then `GCSPUSHM` and `GCSPOPM` encoded as `sys`/`sysl`. Includes simple `puts` for failure output.

Control flow: enable GCS with push permission; on failure print message and exit `KSFT_SKIP`; on success push/pop and exit 0.

State and persistence: process-local GCS state only; no files.

Dependencies and integration: built `-nostdlib` by GCS Makefile; uses raw syscall ABI.

Risks: skips rather than fails if enabling permission is rejected, which is appropriate for missing support but can hide configuration issues.

Test signals: exit 0 means instruction sequence executed; exit 4 indicates skipped setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcspushm.S -->
