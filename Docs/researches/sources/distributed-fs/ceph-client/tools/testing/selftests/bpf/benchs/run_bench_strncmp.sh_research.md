# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_strncmp.sh

Purpose: compares manual versus helper-based BPF string comparison across selected string lengths.

Important APIs and functions: sources `run_common.sh`; nested loops over lengths `1 8 64 512 2048 4095` and benchmark variants `no-helper`/`helper`; calls `summarize`.

Control flow: one benchmark invocation per length/variant pair.

State and persistence: shell-local only; BPF state is per child run.

Dependencies and integration points: relies on `bench_strncmp.c` argp and common hits/drops parser.

Risks: maximum length is close to the target buffer size and depends on BPF skeleton layout; no header/subtitle output may make long logs less grouped; output parsing can drift.

Test signals: rows show throughput for helper and non-helper implementations at each compare length.
