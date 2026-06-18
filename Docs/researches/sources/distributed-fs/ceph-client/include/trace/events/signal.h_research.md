
# sources/distributed-fs/ceph-client/include/trace/events/signal.h

## Purpose
Defines signal-generation and signal-delivery tracepoints used to diagnose process signaling, blocked/ignored signals, signal queueing, and delivery handler behavior.

## Important APIs, Types, and Functions
`TP_STORE_SIGINFO()` normalizes `siginfo_t` values into errno, code, and optional sending pid/uid. The local enum maps trace outcomes such as delivered, ignored, already pending, overflow fail, loss, and wakeup. Events are `signal_generate` and `signal_deliver`.

## Control Flow
Signal code emits `signal_generate` when a signal is generated or queued for a target task, including destination pid, signal number, group flag, result, and siginfo fields. It emits `signal_deliver` when a signal is delivered to userspace with handler pointer and blocked-mask metadata.

## State and Persistence
No signal state is stored here. Trace records copy comm names, pids, signal numbers, siginfo summary, handler pointer, blocked mask, and result code. The records remain available after task signal structures move on.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, task and signal structures, `siginfo_t`, and signal mask helpers. Integrates with process lifecycle debugging, ptrace/seccomp/audit-adjacent diagnostics, and userspace trace consumers.

## Risks
Signal tracing can expose process ids, command names, handlers, and signal metadata. Result semantics are tightly coupled to signal core behavior; adding new outcomes requires updating symbolic mappings. Handler pointers are diagnostic and can be affected by address randomization.

## Test Signals
Signals include kill/tkill/tgkill tests, real-time signal queue overflow, ignored and blocked signals, handler delivery, group signals, ptrace/seccomp interactions, and BPF/ftrace attachment to `events/signal/*`.
