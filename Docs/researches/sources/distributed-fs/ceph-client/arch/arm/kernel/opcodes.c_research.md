# sources/distributed-fs/ceph-client/arch/arm/kernel/opcodes.c

Purpose: provides canonical NOP encoding generation and instruction set helpers for runtime ARM text patching.

Important APIs/types/functions: `__arm_gen_nop` returns a memory-order NOP appropriate to ARM or Thumb-2 builds, using `__opcode_to_mem_arm` or Thumb compose/conversion helpers.

Control flow: build-time configuration selects Thumb-2 32-bit `nop.w` composition or ARM `mov r0, r0` style NOP.

State and persistence: stateless; generated opcodes are persisted by patching callers.

Dependencies and integration: used by jump labels, alternatives, ftrace, and other text patching code through `asm/opcodes.h`.

Risks: width mismatch breaks instruction stream alignment, especially for Thumb-2 patch sites. Test signals include static key transitions, objdump of patched NOPs, and boot on both ARM/Thumb kernels.
