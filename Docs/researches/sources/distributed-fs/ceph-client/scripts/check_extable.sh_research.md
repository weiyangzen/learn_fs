# sources/distributed-fs/ceph-client/scripts/check_extable.sh

## Purpose
`check_extable.sh` validates that relocations from an object’s `__ex_table` section point only to expected executable sections, helping catch invalid exception table entries.

## APIs, Types, And Functions
It uses `file`, `objdump`, `addr2line`, `grep`, `awk`, and shell functions including `find_section_offset_from_symbol()`, `find_symbol_and_offset_from_reloc()`, `find_alt_replacement_target()`, `handle_alt_replacement_reloc()`, `is_executable_section()`, `handle_suspicious_generic_reloc()`, `diagnose()`, and `check_debug_info()`.

## Control Flow
The script exits early for non-ELF files or objects without `__ex_table`. It extracts relocations from `__ex_table`, filters a whitelist of `.text` and `.fixup`, resolves suspicious relocations to section offsets, special-cases `.altinstr_replacement`, warns for unknown executable sections, errors for non-executable targets, and exits nonzero if an error was found.

## State And Persistence
State is shell variables and diagnostic output. No files are modified.

## Dependencies And Integration Points
It depends on binutils output formats and optional debug info for useful `addr2line` output. It integrates with kernel object validation for exception tables.

## Risks And Test Signals
Risks include regex parsing failures, missing debug info reducing diagnostics, and new legitimate faulting sections requiring whitelist updates. Test signals are exit 0 for normal objects and clear warnings/errors for crafted invalid `__ex_table` relocations.
