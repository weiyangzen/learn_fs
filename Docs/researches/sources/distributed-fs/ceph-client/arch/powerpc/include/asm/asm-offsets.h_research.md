# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-offsets.h

Purpose: redirects architecture assembly code to the generated offset definitions used by the Linux build.

Important APIs/types/functions: includes `<generated/asm-offsets.h>`, which contains structure offsets and constants generated from C.

Control flow: no control flow; this is a generated-header bridge.

State and persistence: no state here. Build output persists in the generated include directory.

Dependencies and integration points: used by assembly macros and exception/MMU code needing offsets into `thread_struct`, `pt_regs`, stack frames, and other C structures.

Risks: stale or missing generated offsets can produce assembly that saves/restores the wrong fields. Include ordering matters for assembly files that expect this path.

Test signals: clean PowerPC build from scratch, verify generated offsets are rebuilt when relevant C structures change, and boot-test exception paths that consume stack/register offsets.
