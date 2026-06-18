## sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpsimdmacros.h

Purpose: assembly macro support for saving, restoring, and manipulating FPSIMD/SVE register state.

Important APIs/types/functions: provides macros for vector register loads/stores, FPSIMD register save/restore sequences, and related assembler helpers used by low-level context-switch code.

Control flow: macro expansion emits repeated SIMD register transfer instructions in deterministic register order.

State and persistence: moves architectural FP/SIMD register state to and from task memory buffers.

Dependencies and integration: included by arm64 assembly implementation files for FPSIMD, signal, and context switching.

Risks: register order or offset mistakes corrupt user FP/vector state. Test signals are FPSIMD/SVE signal tests, ptrace register round-trips, and context-switch stress with randomized vector contents.
