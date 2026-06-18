# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_strncmp.c

Purpose: benchmarks BPF string comparison implemented manually versus through the strncmp helper.

Important APIs and functions: argp option `--cmp-str-len` sets comparison length. `strncmp_setup()` opens `strncmp_bench`, fills rodata target with random digits, copies a slightly smaller string into BSS, sets compare length, and loads the skeleton. `strncmp_no_helper_setup()` and `strncmp_helper_setup()` attach alternate BPF programs. Producer triggers the probe with `getpgid`; `measure()` swaps BSS `hits`.

Control flow: validation rejects consumers. Setup prepares deterministic mismatch-at-last-byte test data for the selected length. The producer loop causes repeated BPF comparisons, and common hit reports compute throughput.

State and persistence: random target string and BSS comparison string live in the skeleton. BSS hits reset per sample. No persistent kernel state beyond BPF link/map lifetime.

Dependencies and integration points: depends on `strncmp_bench.skel.h`, libbpf skeleton APIs, `bench.h`, and the kernel helper under test.

Risks: option parsing references `ctx.skel->bss->str` before `ctx.skel` is opened, which relies on generated skeleton field layout in `sizeof` context and can be surprising; random data makes exact input bytes non-reproducible though only length/mismatch pattern matters; invalid long lengths are rejected.

Test signals: `run_bench_strncmp.sh` sweeps lengths for `strncmp-no-helper` and `strncmp-helper`, reporting hit throughput.
