# sources/distributed-fs/ceph-client/arch/riscv/kernel/crash_save_regs.S

Purpose: Saves RISC-V register state into a `pt_regs`-layout buffer during crash handling.

Important APIs/types/functions: Defines `riscv_crash_save_regs`.

Control flow: The assembly stores all integer registers and selected CSRs (`status`, `tval`, `cause`) into offsets from `a0`; it synthesizes `epc` from the current PC using `auipc`.

State and persistence: Writes a crash-time `pt_regs` snapshot consumed by kdump/vmcore tooling.

Dependencies and integration points: Depends on `asm-offsets.h` register offsets, CSR definitions, and crash/kexec paths.

Risks and test signals: The function overwrites the saved `a0` field after using `a0` as the destination base, so offset correctness and calling convention are critical. Test kdump register notes, crash-triggered vmcore analysis, and 32/64-bit builds.
