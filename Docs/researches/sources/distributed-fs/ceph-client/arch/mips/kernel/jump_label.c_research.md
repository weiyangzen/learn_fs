<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/jump_label.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/jump_label.c

### Purpose
`jump_label.c` implements MIPS static-key patching. It rewrites NOP slots into architecture-appropriate unconditional jumps or branches and applies module jump-label NOP initialization.

### Important APIs, Types, And Functions
The main entry is `arch_jump_label_transform(struct jump_entry *e, enum jump_label_type type)`. With modules, `jump_label_apply_nops(struct module *mod)` initializes module entries whose type is NOP. The code uses `union mips_instruction` and ISA-specific constants for MIPS, microMIPS, and MIPS R6 branch encodings.

### Control Flow
For `JUMP_LABEL_JMP`, the transformer validates target alignment and ISA bit, then emits either R6 `bc6`, microMIPS `j32`, or classic MIPS `j`. For NOP it writes zero. The text patch is serialized by `text_mutex`, written as halfwords for microMIPS or a full instruction otherwise, flushed from icache, and unlocked.

### State, Persistence, And Dependencies
The persistent state is patched kernel or module text. Dependencies include `linux/jump_label.h`, `asm/inst.h`, `msk_isa16_mode()`, MIPS ISA revision macros, `text_mutex`, and `flush_icache_range()`.

### Integration Points
The file integrates with Linux static keys and module finalization. `module.c` calls `jump_label_apply_nops()` during module finalization when jump labels are enabled.

### Risks
Jump range and alignment checks are critical. Classic J jumps cannot cross their region boundary, while R6 branch offsets must fit in 26 signed bits. microMIPS requires halfword ordering and ISA-bit preservation. A wrong patch can execute invalid text on every static-key site.

### Test Signals
Enable static keys in built-in and module code, toggle keys repeatedly, load modules with jump entries, test microMIPS and R6 configs, and use runtime branch patch assertions or objdump spot checks for emitted encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/jump_label.c -->
