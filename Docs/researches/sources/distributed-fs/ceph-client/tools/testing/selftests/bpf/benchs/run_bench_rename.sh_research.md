# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_rename.sh

Purpose: runs rename-trigger overhead benchmarks for base, kprobe, kretprobe, raw tracepoint, fentry, and fexit modes.

Important APIs and functions: loops over mode suffixes, invokes `sudo ./bench -w2 -d5 -a rename-$i`, extracts the final throughput field with `tail` and `cut`, and prints aligned rows.

Control flow: sequentially executes six benchmark variants.

State and persistence: shell-only; BPF links are created per child benchmark.

Dependencies and integration points: assumes sudo access, built `./bench`, stable summary format, and supported attach types.

Risks: output extraction is brittle; failures under `set -euo pipefail` abort the script; no shared `run_common.sh` means duplicated parsing logic.

Test signals: aligned rows allow quick comparison of base versus BPF attachment overhead.
