# sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_event.c

Purpose: implements PA-RISC kernel callchain collection for the generic Linux perf event subsystem.

The single exported behavior is `perf_callchain_kernel(struct perf_callchain_entry_ctx *entry, struct pt_regs *regs)`. It uses `struct unwind_frame_info`, `unwind_frame_init_task`, `unwind_once`, `__kernel_text_address`, and `perf_callchain_store`.

Control flow initializes an unwind cursor for `current` and repeatedly unwinds one frame. The loop exits when unwinding fails or returns a zero instruction pointer. For each frame it first verifies that the instruction pointer is a kernel text address, then stores it into the perf callchain buffer. If the address is not kernel text or the perf buffer refuses another entry, the function returns immediately. The `regs` argument is not used; this implementation starts from the current task unwind state rather than explicitly seeding from the sampled register frame.

State is transient and per-sample: unwind cursor contents and entries appended to the perf callchain context. Dependencies are the PA-RISC unwinder, generic perf callchain storage, current task context, and kernel text address validation.

Risks include callchains beginning from the wrong point if ignoring `regs` is inappropriate for interrupt/NMI sampling contexts, truncated stacks when unwinder metadata is missing, early termination on non-kernel text addresses, and architecture unwinder bugs surfacing as missing perf samples. Test signals are `perf record -g` kernel callchains on PA-RISC, unwinder self-tests if available, verifying no user-space addresses appear in kernel callchains, and sane stack traces under interrupt and syscall sampling.
