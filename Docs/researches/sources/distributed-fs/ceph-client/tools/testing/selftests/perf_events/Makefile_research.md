# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/Makefile

Purpose: builds perf event selftest binaries.

Important settings: `CFLAGS` includes kernel headers, `-Wall`, and `-Wl,-no-as-needed`; `LDFLAGS` links pthread. `TEST_GEN_PROGS` contains `sigtrap_threads`, `remove_on_exec`, `watermark_signal`, and `mmap`.

Control flow/integration: inclusion of `../lib.mk` gives standard kselftest build/run behavior.

State/dependencies: no persistent state. Runtime tests depend on `CONFIG_PERF_EVENTS`, perf_event_open permissions, signal delivery, mmap support, and hardware/software event sources.

Risks: perf permissions (`perf_event_paranoid`/capabilities) can cause skips or failures depending on the test. Some tests are timing-sensitive and use signals/forks/threads.

Test signals: build success produces four binaries; runtime results come from kselftest harness in each C file.
