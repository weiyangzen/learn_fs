<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-test.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-test.S

Purpose: assembly SVE and streaming SVE context-switch/signal-restore test. It repeatedly writes/verifies all Z registers, P registers, and FFR, with optional `SSVE` build behavior.

Important APIs and symbols: generated accessors `setz/getz` and `setp/getp`; helpers `pattern`, `setup_zreg`, `setup_preg`, `setup_ffr`, `check_zreg`, `check_preg`, `check_ffr`, signal handlers, `setsignal`, `barf`, `vl_barf`, and `svcr_barf`; `_start` drives the loop. Uses `rdvl`, `rdffr`, `wrffr`, optional `smstart_sm`, and raw syscalls.

Control flow: install handlers, optionally enter streaming mode, validate VL, print PID, loop by generation. Each iteration verifies VL stability, fills Z/P/FFR shadow buffers and registers with PID/register/generation patterns, checks streaming SVCR when built as SSVE, compares all registers, and repeats. SIGUSR1 intentionally corrupts live vector and predicate state; signal return must restore interrupted values.

State and persistence: `.data` contains `zref`, `pref`, `ffrref`, and `scratch`. Registers track PID, generation, register index, and signal count. No files.

Dependencies and integration: built as `sve-test` and likely as `ssve-test` with preprocessor defines. Used by shell stress scripts and `fp-stress`.

Risks: streaming SVE syscalls exit streaming mode, so code must restart it carefully. FFR is skipped in SSVE mode. Signal ucontext offsets and vector-length calculations must match kernel ABI.

Test signals: startup prints vector length and PID; mismatch dumps expected/actual bytes and SVCR for SSVE; clean termination reports iterations and signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sve-test.S -->
