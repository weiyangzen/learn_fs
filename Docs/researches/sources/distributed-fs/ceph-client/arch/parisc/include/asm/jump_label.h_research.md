# sources/distributed-fs/ceph-client/arch/parisc/include/asm/jump_label.h

Purpose: provides PA-RISC static key/jump-label instruction encoding and patch hooks.

Important APIs/types/functions: defines jump-label NOP/branch encoding helpers and `arch_static_branch`/`arch_static_branch_jump` behavior for generic static keys.

Control flow: code initially executes a NOP or branch; when a static key changes, text-patching code rewrites the instruction to flip fast-path control flow.

State and persistence: patched instructions persist in kernel text. Dependencies and integration: depends on `text-patching.h`, alternatives, cache coherency, and generic jump-label code.

Risks and test signals: branch displacement or patching mistakes corrupt hot paths. Test with static key selftests, cacheflush/jump-label toggling, and objdump of generated sites.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
