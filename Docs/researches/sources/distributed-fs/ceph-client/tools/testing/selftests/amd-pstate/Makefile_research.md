# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/Makefile

Purpose: registers AMD P-state shell selftests with kselftest.

Important APIs/types/functions: empty `all` target prevents accidental `run_tests`; normalizes `ARCH`; on x86 adds AMD and Intel pstate tracer scripts to `TEST_FILES`; sets `TEST_PROGS += run.sh`; adds `basic.sh`, `tbench.sh`, and `gitsource.sh`; includes `../lib.mk`.

Control flow: kselftest invokes `run.sh`; files are installed as dependencies.

State and persistence: build/install metadata only.

Dependencies/integration: integrates with top-level selftests and power tracer utilities under `tools/power/x86`.

Risks and test signals: tracer files are only included on x86; non-x86 still installs shell tests but runtime skips are handled by `run.sh`.
