# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/Makefile

Purpose: Builds RISC-V kprobes, instruction decode, simulation, rethook, and uprobe support objects.

Important APIs/types/functions: Lists objects for `kprobes.o`, `decode-insn.o`, `simulate-insn.o`, `rethook.o`, `rethook_trampoline.o`, and optional uprobes.

Control flow: Kbuild selects objects based on probe-related Kconfig options; runtime behavior is in the compiled C/assembly files.

State and persistence: Build metadata only.

Dependencies and integration points: Integrates with Linux kprobes/uprobes/rethook frameworks and RISC-V trap/text patching code.

Risks and test signals: Missing object selection can silently disable probe features. Test builds with kprobes, kretprobes, uprobes, and combinations with modules.
