# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/augmented_raw_syscalls.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/augmented_raw_syscalls.bpf.c

Purpose: this BPF program augments `raw_syscalls` enter/exit events with pointed-to user data so `perf trace` can display filenames, sockaddr data, perf_event_attr contents, timespecs, and configured "beauty" arguments rather than raw pointer values.

Important APIs, maps, and programs: maps include `__augmented_syscalls__` perf-event array, `syscalls_sys_enter`/`syscalls_sys_exit` program arrays, `pids_filtered`, `augmented_args_tmp`, `beauty_map_enter`, and `beauty_payload_enter_map`. Entry augmenters include `sys_enter_connect`, `sys_enter_sendto`, `sys_enter_open`, `sys_enter_openat`, `sys_enter_rename`, `sys_enter_renameat2`, `sys_enter_perf_event_open`, `sys_enter_clock_nanosleep`, and `sys_enter_nanosleep`. Root programs are raw tracepoint `sys_enter` and `sys_exit`.

Control flow: root `sys_enter` filters configured pids, copies the raw syscall arguments into per-CPU scratch storage, attempts generic `augment_sys_enter()` based on `beauty_map_enter`, and falls back to a syscall-number-indexed tail call. Specific augmenters read user memory safely, set size/error fields, align variable-length strings where needed, and emit augmented payloads to the current CPU perf-output event. `sys_exit` tail-calls into exit augmenters but this file mainly provides the enter path and unaugmented fallback.

State and persistence: all state is in BPF maps configured by user space. Scratch payload maps are per-CPU arrays to avoid BPF stack limits. The pid filter map suppresses perf's own helper pids. Program arrays persist tail-call routing until user space updates them.

Dependencies and integration: user space in `bpf_trace_augment.c` loads and attaches only root programs, configures the perf-output map, and exposes program/map fds for perf trace. The BPF code depends on the hand-maintained `vmlinux.h`, BPF helpers for user reads and perf output, and syscall tracepoint layouts.

Risks: verifier constraints drive several bounds tricks; changes in syscall argument ordering or tracepoint ABI would break augmentation. `getpid()` truncates `bpf_get_current_pid_tgid()` to pid_t, which is intentional for current pid matching but should be reviewed for namespace semantics. Failed output returns nonzero so callers may record unaugmented data; silent drops can happen if tail-call maps are not populated. Buffer augmentation is capped at 32 bytes.

Test signals: run `perf trace` for open/openat/rename/connect/sendto/perf_event_open/nanosleep, with beauty-map driven augmentations and pid filters; verify fallback unaugmented events; and test verifier load on supported clang/kernel combinations.
