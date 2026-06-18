# sources/distributed-fs/ceph-client/arch/s390/include/asm/jump_label.h

Purpose: This header implements s390 static-key branch sites for Linux jump labels.

Important APIs/types/functions: `HAVE_JUMP_LABEL_BATCH`, `JUMP_LABEL_NOP_SIZE`, compiler-specific `JUMP_LABEL_STATIC_KEY_CONSTRAINT`, `arch_static_branch()`, and `arch_static_branch_jump()` are defined. The branch sites emit `brcl` instructions and `__jump_table` records.

Control flow: For a false-by-default static branch, code emits a distinguishable `brcl 0,label` nop-like instruction; for jump form it emits `brcl 15,label`. Runtime jump-label patching rewrites those sites based on static-key state using the table metadata.

State and persistence: Persistent state is encoded in kernel text and `__jump_table`; static-key counters live in generic jump-label structures.

Dependencies and integration points: It depends on compiler inline-asm constraints, Linux static keys, and s390 text patching/alternatives code. Perf, tracing, KVM, PAI, and other fast paths consume these branches.

Risks and test signals: Instruction size, table relocation, or constraint errors break runtime patching. Tests should include GCC/Clang builds, static-key selftests, toggling features that use jump labels, and objdump validation of six-byte patch sites.
