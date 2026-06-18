# sources/distributed-fs/ceph-client/arch/parisc/include/asm/kprobes.h

Purpose: defines PA-RISC kprobes instruction slot, breakpoint, and per-probe architecture state.

Important APIs/types/functions: provides `struct arch_specific_insn`, `struct prev_kprobe`, breakpoint constants, `flush_insn_slot`, and architecture handlers for probe preparation and single stepping.

Control flow: kprobes copies an instruction to a slot, patches the original site with a break, handles the trap, executes or emulates the original instruction, then resumes.

State and persistence: probe metadata and patched instructions persist while probes are registered. Dependencies and integration: trap code, instruction decoder, cacheflush, and text patching.

Risks and test signals: branch delay/nullification and PA-RISC instruction semantics make probe emulation delicate. Test with kprobe selftests on branches, calls, and module text.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
