## `sources/distributed-fs/ceph-client/arch/x86/include/asm/GEN-for-each-reg.h`

Purpose: macro include that enumerates general-purpose registers in architectural machine order for 64-bit or 32-bit x86.

Important APIs and content: the includer defines `GEN(name)`, then includes this file to expand over `rax..r15` on 64-bit or `eax..edi` on 32-bit. The order intentionally matches machine encoding/order and is relied upon by generated register tables.

Control flow: no runtime logic; preprocessor generation only.

State and persistence: no state.

Dependencies and integration points: depends on `CONFIG_64BIT` and the includer-provided `GEN` macro. Likely used by register save/restore, ptrace, unwind, or generated asm metadata where ordering matters.

Risks: changing order or names breaks ABI-like assumptions in generated code and register arrays. Adding separators in this file would break macro includers.

Test signals: build all x86 configs, generated register metadata diff, ptrace/perf register indexing tests.
