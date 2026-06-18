# sources/distributed-fs/ceph-client/arch/x86/lib/cmpxchg16b_emu.S

Purpose: emulates a per-CPU `cmpxchg16b %gs:(%rsi)` operation for contexts that need 128-bit compare/exchange semantics on per-CPU data without using the hardware instruction directly.

Important APIs/functions: defines `this_cpu_cmpxchg16b_emu`. Inputs are `%rsi` per-CPU memory location, `%rax:%rdx` old low/high 64-bit value, and `%rbx:%rcx` new low/high 64-bit value. It reports success/failure through the ZF bit in saved EFLAGS, matching compare/exchange conventions.

Control flow: saves flags, disables interrupts, compares both 64-bit halves at the per-CPU address, writes the new halves if both match, and sets ZF in the saved flags. On mismatch it reloads actual memory into `%rax:%rdx` and clears ZF. Finally it restores flags and returns.

State and persistence behavior: modifies only the target per-CPU 16-byte object and transient interrupt state. It has no globals.

Dependencies/integration points: x86-64 per-CPU addressing, processor flags, Linux linkage. Used by per-CPU atomic code paths where local IRQ exclusion is the intended serialization mechanism.

Risks: comment states it is not lock-prefixed and not safe against NMIs. It only serializes local interrupt handlers, not arbitrary concurrent observers. Register ABI and ZF reporting must remain exact because callers inspect flags.

Test signals: per-CPU cmpxchg tests for success/failure values, interrupt-preemption stress, disassembly validation for `%gs` per-CPU addressing, and NMI-safety review for call sites.
