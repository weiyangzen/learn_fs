# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/mkregtable.c

## Purpose

`mkregtable.c` is a small userspace build utility that converts an authorization/register-list text file into a C static bitmap table named `<gpu_prefix>_reg_safe_bm`. The generated table marks unsafe or disallowed register offsets for Radeon command parser validation. It includes a minimal userspace copy of Linux list helpers so it can collect offsets without depending on kernel headers.

## Important APIs, types, and functions

- Embedded list primitives: `struct list_head`, `INIT_LIST_HEAD()`, `__list_add()`, `list_add_tail()`, `list_entry()`, and `list_for_each_entry()` provide just enough doubly linked list behavior for offset collection.
- `struct offset`: stores one parsed register offset and a list node.
- `struct table`: owns the offset list, maximum offset, bitmap entry count, allocated bitmap pointer, and GPU prefix used in generated symbol names.
- `offset_new()`: allocates and initializes one offset node.
- `table_offset_add()`: appends a parsed offset to the table list.
- `table_init()`: initializes an empty table.
- `table_build()`: allocates the bitmap, initializes all entries to `0xffffffff`, and toggles bits corresponding to listed offsets using `t->table[i] ^= m`.
- `table_print()`: emits the generated static `unsigned` array to stdout, four entries per line.
- `parser_auth()`: opens and parses the auth file, extracts the first-line GPU name and last-register value, scans subsequent lines with a POSIX regex, records offsets, updates `offset_max`, and builds the bitmap.
- `main()`: validates the single input argument, runs parser/build, prints generated output, and returns nonzero on failure.

## Control flow

The program expects exactly one argument: an auth file path. It initializes a `struct table`, then `parser_auth()` compiles a regex matching a hex offset followed by a symbolic name, opens the file, reads its first line as `<gpu_name> <last_reg>`, stores the GPU name in a global buffer, and converts the last-register string to an integer. It then loops through the rest of the file until `ftell(file) == end`, applies the regex to each line, parses matching offsets with `strtol()`, allocates `struct offset` entries, appends them, and tracks the maximum offset seen. After parsing, it ensures `offset_max` is at least the declared last register and calls `table_build()`. Finally, `table_print()` writes a C initializer to stdout.

The bitmap size is computed as `((offset_max >> 2) + 31) / 32`, meaning one bit per 4-byte register slot. Starting from all ones, each listed offset flips one bit to zero. The generated table therefore encodes allowed/blocked status by bit position according to the command parser's expected convention.

## State and persistence behavior

Program state is in heap allocations for the offset list and table bitmap plus the global `gpu_name[10]` buffer. No output file is written directly; generated C is printed to stdout for the build system or caller to redirect. The program does not free allocations before exit, which is acceptable for a short-lived generator but relevant for leak checkers.

## Dependencies and integration points

- Uses userspace C/POSIX headers: `sys/types.h`, `stdlib.h`, `string.h`, `stdio.h`, `regex.h`, and `libgen.h` (`libgen.h` appears unused).
- Intended to run during driver source generation/build workflows that transform register auth files into command-parser safe-bitmask tables.
- The generated symbol name depends on the first token of the auth file, so downstream C code must reference the matching `<gpu_prefix>_reg_safe_bm` name.
- Register offset semantics align with Radeon command parser validation, where packet parsers need fast tests for safe register writes.

## Risks and edge cases

- `table_build()` uses XOR to clear bits. Duplicate offsets toggle the same bit twice, turning it back to one, so duplicate auth entries can corrupt the generated safety table.
- Offset nodes and bitmap memory are never freed. This is harmless for normal one-shot use but noisy under sanitizers.
- `regcomp()` resources are not released with `regfree()`, and several failure paths do not close all resources consistently after regex compilation.
- The parser uses a fixed 1024-byte input buffer and simple regex; long lines are truncated and malformed first lines can produce misleading GPU prefix or last-register values.
- `gpu_name[10]` and `%9s` limit the generated prefix to nine characters, which may truncate longer GPU names and change symbol names.
- Error handling after `offset_new()` is missing. A failed allocation is passed to `table_offset_add()` and would dereference NULL.
- `argc` failures call `exit(1)`, while parse failures return `-1` from `main()`, resulting in shell status 255.

## Test signals

- Compile the utility with host CFLAGS and regex library support.
- Run it on representative auth files and compare generated arrays against checked-in expected tables.
- Include duplicate-offset, empty-file, malformed-header, long-line, and high-last-register fixtures to validate parser and bitmap behavior.
- Downstream command parser tests should reject unsafe register writes and accept known-safe writes using the generated bitmap.
