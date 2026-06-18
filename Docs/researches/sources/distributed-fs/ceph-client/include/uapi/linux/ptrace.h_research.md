<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ptrace.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ptrace.h

Purpose: defines generic architecture-independent ptrace request numbers, option/event bits, signal/syscall info structs, seccomp metadata, and register-set access contracts.

Important APIs and types: base requests include trace, peek/poke, continue, kill, singlestep, attach, detach, and syscall. Extended requests include set/get options, siginfo, regset get/set, seize/interrupt/listen, peeksiginfo, sigmask get/set, seccomp filter/metadata, syscall info get/set, and related option/event constants. `struct ptrace_peeksiginfo_args`, `struct seccomp_metadata`, and `struct ptrace_syscall_info` serialize extended data.

Control flow: a tracer attaches or is inherited via `PTRACE_TRACEME`, sets options, resumes/stops tracees, inspects registers/memory/signals, and observes syscall or seccomp stops. The kernel enforces ptrace permission and LSM policy before exposing task state.

State and persistence: ptrace state is per tracee/tracer relationship: stop state, options, event messages, signal masks, and seccomp filter metadata visibility. It ends when tracing detaches or task exits.

Dependencies and integration points: depends on Linux types and architecture regset note types. Integrates with procfs, signal delivery, seccomp, ELF core notes, debuggers, strace, crash dump tooling, CRIU, and architecture register APIs.

Risks and test signals: risks include privilege bypass, stop-state races, regset size handling through iovec, seccomp filter leakage, and arch-specific option drift. Test debugger/strace workflows, seize/interrupt/listen, syscall info entry/exit/seccomp stops, signal mask operations, regset partial buffers, and LSM/Yama permission denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ptrace.h -->
