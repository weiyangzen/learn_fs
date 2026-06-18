# sources/distributed-fs/ceph-client/arch/sparc/kernel/jump_label.c

## Purpose
`jump_label.c` implements SPARC static key text patching, replacing NOPs with unconditional branches and back.

## Important APIs, Types, and Functions
The public architecture hook is `arch_jump_label_transform(struct jump_entry *entry, enum jump_label_type type)`.

## Control Flow and State
For `JUMP_LABEL_JMP`, the function computes target-code offset, validates word alignment, chooses a V9 predicted branch encoding on sparc64 when the displacement fits WDISP19, otherwise uses WDISP22 `ba`, and asserts WDISP22 range. For non-jump it writes SPARC NOP `0x01000000`. The write is protected by `text_mutex` and followed by `flushi()`.

## Persistence and Dependencies
Persistent state is patched kernel text. Dependencies include jump-label core, `text_mutex`, SPARC branch encoding, and instruction-cache flush.

## Integration Points, Risks, and Test Signals
Integration includes static keys across the kernel. Risks are branch displacement overflow, sign/range mistakes, lack of atomic patching beyond mutex protection, and stale icache if `flushi()` is insufficient on a CPU variant. Test signals are static key enable/disable tests, boot with jump labels enabled, and no illegal instruction traps near patched sites.
