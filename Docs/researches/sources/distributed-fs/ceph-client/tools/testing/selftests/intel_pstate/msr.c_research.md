# sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/msr.c

Purpose: `msr.c` is a tiny helper that reads and prints `MSR_IA32_PERF_CTL` (`0x199`) for one CPU. `run.sh` uses it to include requested P-state control evidence in result files.

Important APIs and functions: `main()` parses a CPU number, opens `/dev/cpu/<cpu>/msr`, reads eight bytes at offset `0x199` with `pread()`, and prints `msr 0x199: 0x...`.

Control flow: invalid argument count or parse error returns 1; open failure prints perror and returns 1; otherwise it reads and prints the MSR then returns 0.

State and persistence: read-only access to `/dev/cpu/*/msr`; no persistent output except stdout captured by `run.sh`.

Dependencies and integration points: depends on the x86 msr driver/device node and permissions. It is built by the intel_pstate Makefile and invoked by `run.sh`.

Risks: `pread()` return value is not checked, so unavailable or partial reads can print uninitialized data. `strtol()` range and trailing-character validation are minimal. It only reads CPU 0 in the shell driver, which may not reflect every CPU under test.

Test signals: a valid line containing `msr 0x199:` is appended to each `/tmp/result.<freq>` file by `run.sh`.
