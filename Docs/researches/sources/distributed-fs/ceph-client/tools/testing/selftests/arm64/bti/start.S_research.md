# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/start.S

Purpose: freestanding process entry point for BTI tests.

Important APIs/types/functions: `_start` moves stack pointer to `x0` and branches to C `start`; emits AArch64 feature note.

Control flow: kernel enters `_start`; `_start` passes initial stack/argc pointer to `start()` without libc setup.

State and persistence: no state beyond initial register transfer and ELF note.

Dependencies/integration: linked into both BTI and non-BTI binaries.

Risks and test signals: assumes initial stack layout parsed by `test.c`; no libc initialization is available.
