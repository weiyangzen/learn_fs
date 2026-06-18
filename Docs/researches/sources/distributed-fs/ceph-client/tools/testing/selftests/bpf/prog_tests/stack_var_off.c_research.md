# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stack_var_off.c

Purpose: small test for BPF stack reads/writes through offsets not known statically. It loads `test_stack_var_off`, initializes BSS input values, attaches the probe, triggers it with a short sleep, and checks the computed result.

Control flow is linear: open/load skeleton, set `test_pid` to the current process to filter events, initialize `input[0]=2` and `input[1]=42`, attach, wait, then assert `probe_res == 42`. State is skeleton BSS only; no persistent maps are manipulated by the harness. Dependencies are generated skeleton code, `test_progs.h`, and the BPF side probe firing during `usleep`. Risks are event timing sensitivity and accidental triggering by unrelated processes if PID filtering breaks. Test signals are skeleton load/attach success and final BSS result equality.
