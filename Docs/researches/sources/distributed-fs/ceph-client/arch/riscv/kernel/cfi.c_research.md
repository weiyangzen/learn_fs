# sources/distributed-fs/ceph-client/arch/riscv/kernel/cfi.c

Purpose: Decodes and reports Clang kernel CFI trap failures on RISC-V so indirect-call type violations produce useful diagnostics.

Important APIs/types/functions: `handle_cfi_failure()` is the public trap hook. `decode_cfi_insn()` inspects the compiler-generated `beq` and following `jalr` or compressed `c.jalr` sequence, using RISC-V instruction helpers and `pt_regs`.

Control flow: A breakpoint trap first checks `is_cfi_trap(regs->epc)`. If it is not a CFI trap, the handler returns none. If it is, the code reads nearby kernel instructions with `get_kernel_nofault()`, extracts the expected type from the `beq` source register and the indirect target from the `jalr` source register, then calls the generic CFI reporter.

State and persistence: No persistent state is maintained. It consumes register state from the trap frame and nearby text.

Dependencies and integration points: Integrated with generic `linux/cfi.h`, RISC-V instruction decoders in `asm/insn.h`, breakpoint/trap handling, and bug reporting.

Risks and test signals: The decoder is tightly coupled to the compiler CFI sequence and register extraction layout; compiler codegen changes can degrade reports to no-address failures. Test with Clang CFI enabled, injected bad indirect calls, compressed and normal `jalr` sequences, and fault-injection around invalid text reads.
