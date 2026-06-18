# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/special.h

Purpose: x86 special-section layout constants for exception tables, jump labels, static calls, and alternatives.

Important APIs/types/functions: defines `EX_*`, `JUMP_*`, and `ALT_*` entry sizes and offsets used by generic special parsing.

Control flow: none.

State and persistence behavior: parsed entries create alternative paths and jump-label transformations that affect validation and generated diagnostics.

Dependencies and integration points: consumed by generic `special.c`, x86 `special.c`, disassembly alternative naming, and `check.c` alternative graph construction.

Risks: offsets are ABI-coupled to kernel x86 metadata. Mismatch yields wrong branch targets, alternative lengths, or feature flags.

Test signals: x86 objects using `ALTERNATIVE`, exception tables, and jump labels should parse without "weirdly overlapping alternative" or missing instruction errors.
