# sources/distributed-fs/ceph-client/arch/parisc/include/asm/text-patching.h

Purpose: declares PA-RISC kernel text patching functions used by alternatives, jump labels, ftrace, kprobes, and live instruction updates.

Important APIs/types/functions: declares `patch_text`, `patch_text_multiple`, `__patch_text`, and `__patch_text_multiple`.

Control flow: callers request one or more instruction writes; implementation handles permissions, atomicity expectations, and cache synchronization so CPUs execute the new instructions.

State and persistence: modifies kernel text, which persists until repatched or module unload. Dependencies and integration: used by alternatives, static keys, tracing, and probe subsystems.

Risks and test signals: text patching must synchronize I/D caches and avoid partially visible instructions. Test alternatives, ftrace, jump-label toggling, kprobe registration, and SMP patch stress.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
