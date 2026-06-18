# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/special.h

Purpose: LoongArch layout constants for special kernel metadata sections consumed by generic objtool special-section parsing.

Important APIs/types/functions: defines exception table entry size/offsets, jump label entry size/offsets, and alternative instruction entry size/offsets including original/new length fields.

Control flow: no executable control flow. Generic special parsing uses these constants to read binary entries.

State and persistence behavior: parsed special entries create in-memory `struct special_alt` records that later alter validation paths and alternative CFI propagation.

Dependencies and integration points: included by generic `objtool/special.h` implementation and LoongArch `special.c`; tied to LoongArch kernel structs in `extable.h`, `jump_label.h`, and `alternative.h`.

Risks: stale offsets produce mis-linked alternatives, bad exception targets, or invalid jump-label interpretation. These failures often surface as unresolved instructions or stack layout conflicts rather than obvious parse errors.

Test signals: objtool on LoongArch objects using exception tables, jump labels, and alternatives should produce correct alternative paths without "special: can't find" errors.
