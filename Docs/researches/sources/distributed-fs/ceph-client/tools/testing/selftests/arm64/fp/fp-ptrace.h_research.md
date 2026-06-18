<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.h

Purpose: small shared ABI header between the C and assembly halves of `fp-ptrace`.

Important definitions: defines SVCR bit shifts and masks `SVCR_SM` and `SVCR_ZA`, plus feature flag shifts/masks `HAVE_SVE`, `HAVE_SME`, `HAVE_SME2`, `HAVE_FA64`, and `HAVE_FPMR`.

Control flow and state: no runtime control flow or storage. The numeric bit positions must remain stable because assembly uses `tbz`/`ubfx` on these flags.

Dependencies and integration: included by `fp-ptrace.c` and `fp-ptrace-asm.S`. It bridges C feature detection and assembly register load/save behavior.

Risks: adding features or changing bit positions without updating both sides would silently corrupt test coverage.

Test signals: indirect; correct flags enable or skip corresponding assembly state paths during `fp-ptrace`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace.h -->
