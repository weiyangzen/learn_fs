# sources/distributed-fs/ceph-client/tools/objtool/special.c

Purpose: Defines and parses objtool special sections describing alternatives, jump labels, exception tables, and switch/jump-table metadata.

Important APIs/types/functions: `reloc_to_sec_off`, `get_alt_entry`, `special_get_alts`, `special_entry`.

Control flow: `special_get_alts()` scans known special sections, validates entry sizes, resolves orig/new/key relocations into `struct special_alt`, applies arch adjustment, and returns a list for checker control-flow modeling.

State and persistence behavior: Allocates a per-run list of `special_alt` records; no direct persistence.

Dependencies and integration points: Uses architecture special-section offsets, objtool ELF relocation helpers, arch alternative handlers, and Linux list utilities.

Risks: Section layout constants must match assembler macros; missing relocations or x86 extable offset hacks can mis-model runtime control flow.

Test signals: Objects with `.altinstructions`, `__jump_table`, `__ex_table`, empty sections, bad sizes, missing relocs, and arch-specific alternative handling.

Source coverage: researched from the complete local file (170 lines, 3953 bytes).
