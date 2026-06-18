<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sve.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sve.c

Purpose: tiny helper program that prints the current SVE vector length in bytes.

Important APIs and functions: `main` calls `rdvl_sve()` from `rdvl.S` via `rdvl.h`, then prints the result.

Control flow and state: no persistent state; one helper call, one print, exit 0.

Dependencies and integration: used by `sve-probe-vls.c` and `vec-syscfg.c` to cross-check prctl/procfs vector-length reporting after exec.

Risks: must run only on SVE-capable systems or under a caller that has already skipped unsupported cases.

Test signals: stdout contains one decimal VL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/rdvl-sve.c -->
