<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/cp1emu.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/cp1emu.c

Purpose: Implements the MIPS COP1/FPU instruction emulator, including microMIPS translation, FPU branch/delay-slot handling, register transfer, memory access, arithmetic dispatch, COP1X operations, R6 comparisons, and exception signaling.

Important APIs/types/functions: Public entry `fpu_emulator_cop1Handler()` loops over emulatable FPU instructions. Core helpers include `microMIPS32_to_MIPS32()`, `isBranchInstr()`, `cop1_64bit()`, `cop1_cfc()`, `cop1_ctc()`, `cop1Emulate()`, `fpux_emu()`, and `fpu_emu()`. Register macros handle 32-bit, 64-bit, and hybrid FPR layouts.

Control flow: The handler initializes/saves FPU context, decodes current and next instruction for MIPS or microMIPS, skips NOPs, and calls `cop1Emulate()`. `cop1Emulate()` resolves delay slots, translates microMIPS FPU ops, handles loads/stores/control moves/branches, and delegates arithmetic to `fpu_emu()` or COP1X indexed/FMA operations to `fpux_emu()`. Arithmetic maps instruction function codes to IEEE754 single/double helpers, updates FCSR exception cause/sticky bits, raises SIGFPE when enabled, and writes results only after exception checks.

State and persistence: Mutates `pt_regs` EPC/GPRs, current thread FPU register file, `ctx->fcr31`, emulator stats, and optional fault address. Looping continues only for software-only FPU mode and stops on signals, non-FPU instruction, hardware-FPU boundary, or ISA mode switch.

Dependencies and integration: Uses MIPS branch/delay-slot emulation, user access helpers, perf software events, IEEE754 helpers, CPU feature macros, FPU ownership/context helpers, and debug stat macros.

Risks: Delay-slot and microMIPS translation correctness is critical for precise exceptions. User memory access must return SIGBUS for invalid access and SIGSEGV for page faults. FCSR exception masking must prevent result writeback when SIGFPE is required. Hybrid FPR layouts make register indexing error-prone.

Test signals: Floating-point programs on no-FPU systems should execute through the emulator; denormal/NaN edge cases on hardware-FPU systems should emulate one instruction; R6 compare/branch and microMIPS FPU encodings should produce correct EPC, result, and signal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/cp1emu.c -->
