# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/Makefile

Purpose: builds prctl selftests on native x86 only.

Important APIs/types/functions: under `ifndef CROSS_COMPILE`, normalizes `ARCH` to `x86` and sets `TEST_PROGS` to TSC controls, anonymous VMA naming, and process-name tests.

Control flow: if the normalized architecture is x86, `all` builds the listed programs and includes `../lib.mk`; otherwise no tests are built from this Makefile.

State and persistence behavior: build-only. No runtime state.

Dependencies and integration points: intentionally excludes cross-compile and non-x86 for TSC-dependent tests, though the VMA/name tests are also gated by that condition here.

Risks and test signals: the coarse x86 gating means non-x86 environments will skip even architecture-neutral prctl tests in this source version.
