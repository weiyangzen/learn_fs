# sources/distributed-fs/ceph-client/arch/loongarch/kernel/unaligned.c

Purpose: emulates LoongArch unaligned load/store faults for integer and floating-point accesses that the hardware or current CPU mode did not complete directly. It is the C policy layer above the byte-wise helpers in `arch/loongarch/lib/unaligned.S`.

Important APIs, types, and functions: `emulate_load_store_insn(struct pt_regs *regs, void __user *addr, unsigned int *pc)` is the external entry point. `read_fpr()` and `write_fpr()` use inline assembly to move values between GPRs and FPRs, with 32-bit and 64-bit variants. It depends on `union loongarch_instruction`, opcode helpers from `asm/inst.h`, `unaligned_read()`, `unaligned_write()`, `compute_return_era()`, `fixup_exception()`, and FPU ownership helpers.

Control flow: the handler records a software emulation perf event, fetches the trapped instruction via `__get_inst()`, decodes supported immediate, pointer, indexed, and FP load/store opcodes, validates access size and user `access_ok()`, then either reads bytes into the destination register or writes the register value back to memory. Successful emulation advances ERA with `compute_return_era()`. Memory helper faults first try exception-table fixup, then kill kernel faults or signal userspace with `SIGSEGV`; unsupported instructions signal `SIGBUS`.

State and persistence: under `CONFIG_DEBUG_FS`, it increments `unaligned_instructions_user` or `unaligned_instructions_kernel` and exposes both counters through `arch_debugfs_dir`. FP state may be written either to live hardware FPRs or `current->thread.fpu` depending on `is_fpu_owner()`.

Dependencies and integration points: integrated with the LoongArch exception path for ALE handling, Linux perf software events, debugfs, signal delivery, exception tables, and the architecture FPU save area. It relies on the assembly helper returning zero or `-EFAULT`-style failure.

Risks: decoder coverage must exactly match the ISA encodings that can fault on unaligned access; missing an opcode becomes `SIGBUS`. FP handling is sensitive to FPU ownership and register width. Kernel-mode faults depend on valid exception-table fixups; otherwise the kernel dies. The `sign` flag is meaningful for reads but harmlessly set on stores.

Test signals: unaligned user integer and FP load/store tests should verify sign extension, unsigned loads, indexed loads, and PC advancement. Kernel selftests or fault injection should cover exception-table recovery. Debugfs counters and `PERF_COUNT_SW_EMULATION_FAULTS` provide runtime observability.
