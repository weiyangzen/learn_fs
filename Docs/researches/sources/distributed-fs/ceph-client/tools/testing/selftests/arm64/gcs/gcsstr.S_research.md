<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcsstr.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcsstr.S

Purpose: standalone assembly smoke test that enables GCS write permission and executes a GCS store instruction.

Important APIs and symbols: `_start` enables `PR_SHADOW_STACK_ENABLE | PR_SHADOW_STACK_WRITE`, reads `GCSPR_EL0`, subtracts one slot, and emits encoded `GCSSTR x1, x0`.

Control flow: enable GCS write permission; on failure print and exit skip; on success perform store and exit 0.

State and persistence: writes process shadow stack memory only; no files.

Dependencies and integration: built `-nostdlib`, uses raw syscall and encoded GCS instruction.

Risks: direct GCS store targets `GCSPR_EL0 - 8`; incorrect pointer assumptions would fault. Like `gcspushm`, setup failure exits as skip.

Test signals: exit 0 for successful instruction use, 4 for skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcsstr.S -->
