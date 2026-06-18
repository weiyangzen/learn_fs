# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/Makefile

Purpose: this Makefile selects ARM64 probe support objects based on kernel configuration. It binds the shared decoder/simulator code into both kprobes and uprobes builds.

Important build rules: `obj-$(CONFIG_KPROBES)` includes `kprobes.o`, `decode-insn.o`, `kprobes_trampoline.o`, and `simulate-insn.o`. `obj-$(CONFIG_UPROBES)` includes `uprobes.o`, `decode-insn.o`, and `simulate-insn.o`.

Control flow and integration: there is no runtime control flow, but the object composition is significant. Kprobes need the text patching handlers and kretprobe trampoline; uprobes reuse the same instruction classification and simulation layer without the kernel text breakpoint machinery.

Dependencies: depends on Kbuild config symbols and on the C/assembly files in the same directory. Shared objects must remain free of kprobes-only dependencies unless protected by `CONFIG_KPROBES`, because they are also linked for uprobes.

Risks: adding a dependency to `decode-insn.o` or `simulate-insn.o` that only exists under one probe config can break the other. Omitting `kprobes_trampoline.o` breaks kretprobes, while omitting simulator support rejects branch/literal instructions that cannot run from XOL slots.

Test signals: build matrices for `CONFIG_KPROBES`, `CONFIG_UPROBES`, both, and neither. Runtime validation comes from kprobe/uprobe selftests, kretprobe return trapping, and probe registration on simulated versus single-stepped instructions.
