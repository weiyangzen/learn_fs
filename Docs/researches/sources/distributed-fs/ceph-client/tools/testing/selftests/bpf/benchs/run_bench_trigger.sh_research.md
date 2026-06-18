# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_trigger.sh

Purpose: runs default or user-specified trigger benchmark variants and prints compact throughput rows.

Important APIs and functions: defines default tests for usermode/kernel/syscall counting and common tracing attach types; allows CLI override; reads producer count from `PROD_CNT`; invokes `sudo ./bench -w2 -d5 -a -p$p trig-$t`.

Control flow: selects test list, selects producer count, sequentially runs each trigger variant, and extracts the final throughput with `tail`/`cut`.

State and persistence: no persistent state beyond environment variable use.

Dependencies and integration points: depends on `bench_trigger.c` names, sudo, built `./bench`, and stable final summary formatting.

Risks: all-symbol kprobe tests can be expensive or unsupported; parser is brittle; default includes feature-sensitive attach kinds that may fail on some kernels.

Test signals: per-trigger row throughput enables quick overhead comparison across attach technologies.
