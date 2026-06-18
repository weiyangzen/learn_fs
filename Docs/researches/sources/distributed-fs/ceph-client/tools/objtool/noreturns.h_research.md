# sources/distributed-fs/ceph-client/tools/objtool/noreturns.h

Purpose: Lists functions objtool treats as non-returning for control-flow validation.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: The checker includes this generated/static list when annotating calls that terminate execution instead of returning to the next instruction.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Integrates with objtool call graph and kernel symbol naming.

Risks: Missing entries create false unreachable/return warnings; stale entries can hide real fallthrough.

Test signals: Control-flow validation around panic/BUG/exit-style calls and sync with kernel annotations.

Source coverage: researched from the complete local file (56 lines, 1633 bytes).
