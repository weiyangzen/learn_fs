# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bug.h

Purpose: implements PowerPC architecture-specific BUG/WARN emission and declares exception/fault handling helpers.

Important APIs/types/functions: assembly macro `EMIT_BUG_ENTRY`, C `_EMIT_BUG_ENTRY`, `BUG_ENTRY`, `BUG()`, `BUG_ON()`, `WARN_ON()`, `EMIT_WARN_ENTRY`, and declarations for `hash__do_page_fault()`, `bad_page_fault()`, `emulate_single_step()`, `_exception()`, `_exception_pkey()`, `die()`, `die_mce()`, `die_will_crash()`, and panic kmsg flush hooks.

Control flow: BUG/WARN macros emit a trap instruction (`twi`/`tdnei` style) followed by an entry in `__bug_table`. Constant conditions are optimized at compile time where possible; nonconstant PPC64 `BUG_ON`/`WARN_ON` emit conditional trap instructions.

State and persistence: bug metadata persists in the built kernel's `__bug_table` and optional `.rodata` file strings. Runtime state is exception handling and warning tainting managed elsewhere.

Dependencies and integration points: depends on asm offsets for assembler mode, asm compatibility, generic bug handling, exception tables, fault handlers, and panic infrastructure.

Risks: bug table entry layout must match generated offsets and generic bug parser expectations. Trap instruction selection must be valid for 32/64-bit builds. Incorrect WARN flags can misreport taints.

Test signals: `CONFIG_BUG` and `CONFIG_DEBUG_BUGVERBOSE` builds, LKDTM BUG/WARN tests, module bug table decoding, and exception path tests for conditional traps.
