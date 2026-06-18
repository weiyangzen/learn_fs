## sources/distributed-fs/ceph-client/arch/arm64/include/asm/jump_label.h

Purpose: arm64 static key/jump label implementation for patchable branches.

Important APIs/types/functions: defines `HAVE_JUMP_LABEL_BATCH`, `JUMP_LABEL_NOP_SIZE`, `JUMP_TABLE_ENTRY`, `ARCH_STATIC_BRANCH_ASM`, `arch_static_branch`, and `arch_static_branch_jump`.

Control flow: inline assembly emits a NOP or branch placeholder plus a jump table entry. Static key updates patch the instruction to branch or fall through.

State and persistence: jump table entries and patched text persist while keys change.

Dependencies and integration: depends on instruction size/encoding and static key core. Used by cpufeature alternatives, tracepoints, sched features, networking, and many static branches.

Risks: bad instruction size or table entries corrupt text patching. Test signals are jump_label selftests, tracepoint toggling, static key stress, module load/unload, and objdump validation.
