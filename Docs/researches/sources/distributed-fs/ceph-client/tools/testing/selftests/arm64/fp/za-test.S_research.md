<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-test.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-test.S

Purpose: assembly SME ZA context-switch and signal-restore test. It fills every ZA horizontal vector with deterministic data and verifies preservation across syscalls, preemption, and signal delivery.

Important APIs and symbols: helpers `pattern`, `setup_za`, `memcmp`, `check_za`, signal handlers, `setsignal`, `barf`, `vl_barf`, and `svcr_barf`. Uses `smstart_za`, `rdsvl`, `_ldr_za`, `_str_za`, `sched_yield`, and raw signal/syscall interfaces.

Control flow: install handlers, enable ZA, validate streaming vector length, get PID, then loop by generation. Each iteration checks VL stability, fills all ZA rows with row/generation/PID/lane patterns, yields, checks SVCR is ZA=1/SM=0, stores and compares every ZA row, then repeats.

State and persistence: `.data` has large `zaref` and `scratch` buffers sized for max VL. Architectural ZA is the target state. No files.

Dependencies and integration: uses `assembler.h`, `asm-offsets.h`, `sme-inst.h`; launched by `za-stress` and `fp-stress`.

Risks: large static buffer sized for 2048-bit VL squared. Signal handler intentionally resets ZA and relies on signal return to restore interrupted state. Any SVCR/VL ABI change affects the test.

Test signals: startup prints streaming mode, vector length, and PID; mismatch dumps expected/actual row data and SVCR; clean termination reports iterations and signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-test.S -->
