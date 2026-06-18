# sources/distributed-fs/ceph-client/tools/perf/util/bpf_trace_augment.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_trace_augment.c

Purpose: this file is the user-space loader and control surface for `perf trace` raw syscall augmentation BPF.

Important APIs and functions: `augmented_syscalls__prepare()` opens, adjusts autoattach, loads, and attaches the augmented raw syscall skeleton. `augmented_syscalls__create_bpf_output()` adds a `bpf-output` evsel named `__augmented_syscalls__`. `augmented_syscalls__setup_bpf_output()` populates the BPF perf-event array with output fds per CPU. `augmented_syscalls__set_filter_pids()` fills the pid filter map. `augmented_syscalls__get_map_fds()` returns program-array and beauty-map fds. `augmented_syscalls__unaugmented()` and `augmented_syscalls__find_by_title()` expose BPF programs for map population. `augmented_syscalls__cleanup()` destroys the skeleton.

Control flow: prepare disables autoattach for all syscall-specific programs so only root `sys_enter` and `sys_exit` attach directly; those root programs later tail-call into configured maps. Output setup is separated from prepare because perf must first create/open the bpf-output evsel and have per-CPU fds.

State and persistence: static `skel` and `bpf_output` store session state. BPF maps retain tail-call and pid-filter configuration until cleanup.

Dependencies and integration: depends on libbpf skeleton `augmented_raw_syscalls`, perf evlist parsing/opening, CPU fd arrays, and trace augment code that populates tail-call maps and beauty maps.

Risks: `augmented_syscalls__prepare()` returns load errors without destroying an opened skeleton. `augmented_syscalls__setup_bpf_output()` assumes `bpf_output->core.fd` is indexed by CPU id, matching existing perf fd array conventions. Failure to populate program arrays means root programs filter/drop rather than augment many syscalls.

Test signals: run perf trace with syscall augmentation enabled, verify bpf-output map fds per CPU, set pid filters, populate tail calls for known syscalls, and unload/reload repeatedly to detect leaks.
