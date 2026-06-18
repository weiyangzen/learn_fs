## sources/distributed-fs/ceph-client/arch/loongarch/kernel/rethook_trampoline.S

### Purpose
`rethook_trampoline.S` is the LoongArch return-hook trampoline. It saves a full base-register frame, calls the C rethook callback with a `pt_regs` pointer, uses the callback result as the real return address, restores registers and privilege/interrupt bits, and jumps back.

### Important APIs, Types, And Functions
The exported code symbol is `arch_rethook_trampoline`. Local macros `save_all_base_regs` and `restore_all_base_regs` use `cfi_st`/`cfi_ld` and `PT_*` offsets to save GPRs and selected CRMD bits. It calls `arch_rethook_trampoline_callback`.

### Control Flow
On entry, the trampoline allocates `PT_SIZE`, saves base registers and CRMD PLV/IE bits, records caller SP in `PT_R3`, passes `sp` as `pt_regs`, and calls the C callback. The callback returns the original or modified return address in `a0`; the trampoline moves it to `ra`, restores all saved registers and CRMD masked bits, drops the frame, and `jr ra`.

### State, Persistence, And Dependencies
Only stack-frame state persists during trampoline execution. The code depends on exact `struct pt_regs` offsets, CFI macros, LoongArch CSR access, and `rethook.c` callback semantics.

### Integration Points
`arch_rethook_prepare` installs this symbol into `regs->regs[1]`. Generic rethook/kretprobe code consumes the constructed `pt_regs`.

### Risks
All register save/restore offsets must match `pt_regs`; missing a live register can corrupt the interrupted function. Restoring CRMD PLV/IE bits with `csrxchg` changes privilege/interrupt state and must be limited to the intended mask. The trampoline has undefined unwind hints, so stack traces through it may be limited.

### Test Signals
Kretprobe/rethook stress tests should verify preserved arguments, return values, stack pointer, CRMD interrupt state, and nested hooks. Objtool/unwind diagnostics should be checked for this nonstandard control-flow path.
