# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpf_syscall_macro.c

Purpose: `test_bpf_syscall_macro.c` validates BPF syscall kprobe argument extraction macros, including normal `PT_REGS_PARM*`, CO-RE variants, `BPF_KPROBE_SYSCALL`, architecture-specific fourth-argument handling on x86_64, and a six-argument syscall case using `splice()`.

Important APIs/types/functions: `test_bpf_syscall_macro()` opens, loads, and attaches `bpf_syscall_macro.skel.h`. It sets `skel->rodata->filter_pid` to the current process, calls `prctl()` with known arguments, checks BSS fields filled by the BPF program, then calls `splice()` with deliberately invalid fds but known pointer/value arguments and checks captured BSS fields. It uses `SPLICE_F_NONBLOCK`, `loff_t` offsets, and errno assertion on the failed syscall.

Control flow: the skeleton is opened first so rodata can be set before load. After attach, `prctl()` triggers the monitored syscall path. Assertions compare classic and CO-RE macro outputs. On x86_64, values captured from `cx` for arg4 are expected not to match because syscall arg4 uses a different register convention; the corrected arg4 fields must match. The `splice()` call is expected to fail with `EBADF` while still triggering BPF argument capture for all six arguments. Cleanup always destroys the skeleton.

State and persistence: transient state is the attached kprobe programs, rodata PID filter, BSS argument capture fields, local offset variables, and errno from `splice()`. No persistent files or kernel objects remain after skeleton destruction.

Dependencies: depends on generated `bpf_syscall_macro.skel.h`, kprobe support for syscall entry points used by the skeleton, syscall register conventions, CO-RE support, and architecture conditionals for x86_64.

Integration points: this file is a direct userspace trigger for BPF-side macro tests. It ensures BPF tracing helper macros used by many kprobe programs interpret syscall arguments correctly across regular and CO-RE accessors.

Risks: syscall wrappers and register conventions are architecture-specific; the file handles the known x86_64 arg4 caveat but other architectures depend on skeleton-side support. Kprobe attachment names can vary with kernel config. The `splice()` pointer comparisons store userspace addresses as `__u64`, which is expected for the test but assumes no pointer tagging incompatibility.

Test signals: expected signals are successful skeleton open/load/attach, matching prctl args 1/2/3/4/5 in corrected fields, x86_64 mismatch only for the intentionally wrong cx arg4 fields, matching `BPF_KPROBE_SYSCALL` fields, `splice()` returning `-1` with `-EBADF`, and exact capture of splice fd, pointer, length, and flags arguments.
