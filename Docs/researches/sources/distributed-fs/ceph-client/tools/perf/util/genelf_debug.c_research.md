# sources/distributed-fs/ceph-client/tools/perf/util/genelf_debug.c

## Purpose

`genelf_debug.c` adds minimal DWARF debug sections to generated JIT ELF files. It converts jitdump debug entries into `.debug_line`, `.debug_info`, and `.debug_abbrev` data.

## Important APIs, Types, and Functions

The public function is `jit_add_debug_info`. Static helpers implement a growable `buffer_ext`, LEB128 emission, DWARF opcode emission, line-table state transitions, compilation-unit creation, abbreviation creation, and debug-entry preprocessing. Key internal structures mirror DWARF line and compilation-unit headers.

## Control Flow

`jit_add_debug_info` initializes three dynamic buffers, calls `jit_process_debug_info`, then creates three libelf sections and assigns their buffers as ELF data before `elf_update`. `jit_process_debug_info` normalizes debug-entry addresses relative to the original code address, appends one compilation unit pointing at the current line-table offset, emits line-table rows from debug entries using special opcodes when possible, and emits a minimal compile-unit abbreviation.

## State and Persistence Behavior

The generated DWARF bytes persist in the ELF being written. Temporary buffers grow by doubling and are freed after `elf_update`. The function mutates incoming `debug_entry` addresses in place by subtracting `code_addr`, so callers should not expect the debug array to remain unchanged.

## Dependencies and Integration Points

It depends on libelf, DWARF constants, jitdump debug-entry layout, `genelf.h` section-name offsets/type aliases, Linux packed/compiler helpers, and zalloc. It is called from `genelf.c` when libdw support and debug entries are available.

## Risks and Edge Cases

In-place address normalization is a notable side effect. The implementation targets simple DWARF2 32-bit unit lengths and comments that >4GB debug data is unsupported. Several `buffer_ext_add` calls ignore allocation failures. Filename handling has a repeated-name marker convention, and line opcode range choices are static guesses. The `.debug_abbrev` section comment labels `sh_name = 76` as `.debug_info`, but the offset is `.debug_abbrev`.

## Test Signals

Tests should feed multiple files/lines, repeated-name markers, large buffers, and nonmonotonic addresses; validate with `readelf --debug-dump`, ensure perf resolves source lines for JIT samples, and run allocation-failure or sanitizer tests for buffer growth paths.
