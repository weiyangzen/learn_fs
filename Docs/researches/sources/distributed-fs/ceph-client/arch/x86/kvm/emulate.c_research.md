# sources/distributed-fs/ceph-client/arch/x86/kvm/emulate.c

## Purpose

`emulate.c` is KVM's generic x86 instruction decoder and emulator. It decodes instruction bytes into `struct x86_emulate_ctxt`, performs architectural mode, privilege, segment, memory, FPU, and intercept checks, executes supported instructions, and writes guest-visible state back through `x86_emulate_ops`.

## Important APIs, Types, And Functions

- Decode flags and operand encodings: `Op*`, `Dst*`, `Src*`, `ModRM`, `Lock`, `Priv`, `Prot`, `String`, `PageTable`, `Intercept`, `CheckPerm`, `Sse`, `Mmx`, `Avx`, `ShadowStack`, and `IsBranch`.
- Decode table types and tables: `struct opcode`, grouped/prefix/escape table types, `opcode_table`, `twobyte_table`, and `opcode_map_0f_38`.
- Public entry points: `x86_decode_insn()`, `x86_emulate_insn()`, `init_decode_cache()`, `emulator_task_switch()`, `emulate_int_real()`, `x86_page_table_writing_insn()`, `emulator_can_use_gpa()`, and register-cache helpers.
- Memory and address helpers: `__linearize()`, `linearize()`, `segmented_read()`, `segmented_write()`, `segmented_cmpxchg()`, `read_emulated()`.
- Execution handlers: `em_*` functions for ALU, stack, branches, segment loads, task switches, system calls, CR/DR/MSR operations, CPUID, I/O, FPU/SIMD state, and string instructions.

## Control Flow

`x86_decode_insn()` initializes fetch state, determines default operand/address sizes from mode and CS attributes, consumes prefixes, selects opcode tables, resolves group/prefix/escape/mode indirections, rejects unsupported encodings, adjusts mode-specific operand sizes, decodes ModR/M/SIB and absolute addressing, sets segment defaults, and fetches register/immediate operands.

`x86_emulate_insn()` validates LOCK, undefined/no64, SIMD/FPU prerequisites, AVX XCR0, MMX pending x87 faults, intercepts, protected/privileged rules, permission callbacks, and REP string termination. It then reads memory operands, executes a table-provided handler or switch-based simple instruction, writes back source/destination operands, updates string registers and repeat counts, commits RIP, or records exceptions/intercepts.

Segment loads and far transfers use `__load_segment_descriptor()`, `assign_eip()`, and specialized call/ret/syscall/sysenter/sysexit handlers. Task switching saves old TSS state, loads new 16-bit or 32-bit TSS state, updates busy/NT/TS/debug state, and writes registers back when successful.

## State And Persistence

All decode/execution state is carried in `struct x86_emulate_ctxt`: opcode flags, operands, effective IP, EFLAGS, exception state, register-cache bitmaps, read caches, prefixes, intercept metadata, and callbacks. Persistent guest changes happen only through `ctxt->ops` callbacks for GPRs, memory, segments, descriptor tables, CR/DR/MSR/XCR, PIO, FPU state, interruptibility, SMM, halt, and TLB invalidation.

Read caches support MMIO re-emulation ordering and PIO read-ahead. FPU/SIMD access is transient and protected with `kvm_fpu_get()`/`kvm_fpu_put()`.

## Dependencies And Integration Points

The emulator depends on `kvm_emulate.h`, `kvm_cache_regs.h`, `fpu.h`, `tss.h`, `mmu.h`, `pmu.h`, and x86 architecture headers. It integrates with VMX/SVM intercept logic through table metadata and `ctxt->ops->intercept()`, with CPUID through `ctxt->ops->get_cpuid()`, and with MMU page-table tracking through the `PageTable` decode flag.

## Risks And Maintenance Notes

- Decode table flags are security and correctness critical; missing privilege, lock, intercept, or page-table flags can change guest-visible fault ordering or MMU behavior.
- The emulator rejects many unsupported cases, including parts of protected-mode interrupt/IRET, 64-bit FXSAVE/FXRSTOR formats, and CET shadow-stack/IBT affected instruction emulation.
- Segment loading and far transfers can partially update memory or descriptors before later faults.
- REP string restart depends on stable decode, read-cache replay, RF handling, and correct RSI/RDI/RCX updates.
- Inline assembly ALU helpers and FPU/SIMD access depend on correct exception-table, EFLAGS, CR0/CR4/XCR0, and FPU locking behavior.

## Test Signals

Exercise MMIO decode and restart, page-table writes, LOCK/cmpxchg, REP strings, prefix/REX/VEX decoding, ModR/M/SIB/RIP-relative addressing, segment faults, privilege checks, CR/DR/MSR/CPUID/I/O behavior, FXSAVE/FXRSTOR and SIMD moves, real-mode interrupts, task switches, syscall/sysenter/sysexit, CET rejection, and fuzzed instruction bytes against hardware where feasible.
