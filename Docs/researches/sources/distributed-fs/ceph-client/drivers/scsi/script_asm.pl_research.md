# sources/distributed-fs/ceph-client/drivers/scsi/script_asm.pl

## Purpose
`script_asm.pl` is a Perl assembler for NCR/Symbios SCSI SCRIPTS programs. It reads SCRIPTS-like assembly from standard input and emits C header files containing a `u32 SCRIPT[]` array, label and external patch metadata, entry-point defines, and an undef header for generated symbols.

## Important APIs, Types, And Functions
The script is organized around global tables and parser helpers. `%scsi_phases`, `%operators`, and `%registers` define instruction encodings, with alternate register/operator sets under `-ncr7x0_family`. `%symbol_values`, `%symbol_references`, and `%forward` implement a single-pass symbol table with later patching. `patch()` modifies byte fields inside generated 32-bit words. `parse_value()` records absolute/relative/external references and patches immediate values. `parse_conditional()` encodes IF/WHEN conditional clauses for transfer-control instructions. The main loop parses labels, `ABSOLUTE`, `RELATIVE`, `EXTERNAL`, `ENTRY`, `MOVE`, `SELECT`, `RESELECT`, `WAIT`, `SET`, `CLEAR`, `JUMP`, `CALL`, `INT`, `RETURN`, `INTFLY`, `DISCONNECT`, and `NOP`.

## Control Flow
Command-line arguments choose output header paths, while Perl `-s` options can set flags such as `-prefix` or `-ncr7x0_family`. For each input line, the script stores the original line for optional comments, strips semicolon comments, parses declarations or instructions, appends one or more 32-bit words to `@code`, and advances the instruction address. After input, it rejects unresolved forward references, patches absolute symbols, records external patches, resolves label references as absolute or 24-bit relative offsets, then writes `script.h` and `scriptu.h` style outputs.

## State And Persistence
All assembler state is in global Perl variables for one process run: generated words, symbol tables, label/entry/external lists, source listing comments, address, and line number. Persistent outputs are the two generated header files. No repository state is modified except those output paths when the script is run.

## Dependencies And Integration Points
The script depends on `/usr/bin/perl -s` behavior, C consumers expecting `static u32 <prefix>SCRIPT[]`, patch arrays, and generated `#define` names, and SCSI driver build rules that pipe script source into it. It integrates with NCR53c7xx/8xx-style drivers that patch absolute and external addresses after including the generated header.

## Risks And Edge Cases
The parser relies heavily on regular expressions, global variables, and `eval` for numeric expressions, so malformed input can fail late or unexpectedly. It is single-pass and intentionally lacks features such as `PASS`, data-relative `REL`, and multi-script starts. Output files are opened directly for writing rather than atomically. Several diagnostics use stale variable names in error text. Relative addressing is limited to 24 bits and external references must be full-word absolute references. The script emits generated C that depends on `u32` and compiler support for `__attribute((unused))`.

## Test Signals
Signals include assembling known NCR script sources for both default and `-ncr7x0_family` modes, verifying generated instruction words and patch arrays, forward and undefined-symbol diagnostics, absolute/relative/external patch handling, conditional forms with phases/data/masks, `MOVE MEMORY` three-word output, prefix namespacing, generated undef header content, and build success of C drivers that include the generated headers.
