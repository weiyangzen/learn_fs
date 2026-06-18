<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/patching.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/patching.c

## Purpose
Implements safe single-instruction runtime patching for OpenRISC kernel text.

## Important APIs, Types, And Functions
`patch_map()` maps core text through `__pa_symbol()` or vmalloc text through `vmalloc_to_page()` into a fixmap slot. `__patch_insn_write()` serializes with `patch_lock`, writes via `copy_to_kernel_nofault()`, invalidates I-cache, and clears the fixmap. `patch_insn_write()` validates 4-byte alignment.

## Control Flow
Callers request an instruction write. The implementation maps the physical page writable through `FIX_TEXT_POKE0`, writes one 4-byte instruction, invalidates local I-cache over that word, unmaps, and unlocks.

## State And Persistence
Mutates executable memory and transient fixmap PTEs. Uses a global raw spinlock.

## Dependencies And Integration Points
Depends on fixmap, section classification, vmalloc pages, I-cache maintenance, and `text-patching.h`. Used by jump labels.

## Risks
Only local I-cache invalidation occurs here; callers needing cross-CPU sync must arrange it. Unaligned addresses fail. Incorrect page classification or fixmap use can corrupt unrelated text.

## Test Signals
Jump-label patching after boot, vmalloc/module text patching, alignment failure tests, and SMP instruction visibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/patching.c -->
