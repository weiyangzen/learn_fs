# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/run_bench_uprobes.sh

Purpose: runs user-space trigger overhead benchmarks for uprobes, uretprobes, and USDT probes.

Important APIs and functions: loops over `usermode-count`, `syscall-count`, `{uprobe,uretprobe}-{nop,push,ret,nop5}`, `usdt-nop`, and `usdt-nop5`; invokes `sudo ./bench -w2 -d5 -a trig-$i`; extracts final summary.

Control flow: sequential fixed matrix, one line per benchmark variant.

State and persistence: shell-only.

Dependencies and integration points: depends on x86-only variants being built when requested, `bench_trigger.c` benchmark names, sudo, and stable output format.

Risks: `nop5` and USDT variants are guarded in C for x86 but the shell script always lists them; non-x86 environments can fail; output parsing is duplicated and fragile.

Test signals: compact rows compare function-body instruction choice, retprobe overhead, and USDT overhead.
