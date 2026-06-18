<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-test.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-test.S

Purpose: assembly FPSIMD context-switch and signal-restore stress test. It writes unique patterns to all 32 V registers and verifies they survive syscalls, preemption, and signals.

Important APIs and symbols: `_start` is the entry. Accessor functions are generated with `define_accessor setv/getv`. Helpers include `pattern`, `setup_vreg`, `memcmp`, `check_vreg`, `irritator_handler`, `tickle_handler`, `terminate_handler`, `setsignal`, and `barf`. It uses raw `rt_sigaction`, `getpid`, `sched_yield`, `kill`, and `exit` syscalls.

Control flow: install signal handlers, validate fixed 128-bit vector length, get PID, then loop by generation. Each iteration fills V registers and shadow memory with PID/register/generation/lane patterns, yields, reads each register back into scratch, compares against shadow memory, and increments generation. SIGUSR1 intentionally corrupts live V registers in the handler; signal return should restore interrupted state.

State and persistence: `.data` contains `vref` and `scratch`. Registers x20-x23 hold PID, register index/generation, and signal counts. No files.

Dependencies and integration: uses `assembler.h`, `asm-offsets.h`, raw Linux syscall numbers, and optional `enable_gcs` macro for GCS-compatible entry. Invoked by `fpsimd-stress` and `fp-stress`.

Risks: assumes signal-frame offsets from `asm-offsets.h`; if kernel signal ABI or helper macros drift, false failures or crashes can occur. The test exits via SIGABRT on mismatch.

Test signals: prints vector length and PID at startup; clean SIGTERM prints iteration and signal counts; mismatch dumps expected and actual bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fpsimd-test.S -->
