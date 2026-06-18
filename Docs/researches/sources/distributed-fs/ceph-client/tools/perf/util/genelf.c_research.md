# sources/distributed-fs/ceph-client/tools/perf/util/genelf.c

## Purpose

`genelf.c` writes a synthetic ELF shared object for JITed code captured by perf jitdump support. The generated ELF contains executable code, symbol/string tables, a GNU build ID, optional unwind sections, and optional DWARF debug info.

## Important APIs, Types, and Functions

The public function is `jit_write_elf`. Static data includes the section-name string table, a two-entry symbol table, and a build-ID note. `jit_add_eh_frame_info` adds `.eh_frame` and `.eh_frame_hdr` sections. `blake2s_update_tagged` feeds tagged code/symbol/string inputs into the build-ID hash to avoid tuple ambiguity.

## Control Flow

`jit_write_elf` initializes libelf, starts an ELF write on the fd, creates ELF/program headers, writes a loadable `.text` section, hashes code, optionally adds unwind sections after aligned text, creates `.shstrtab`, `.symtab`, `.strtab`, computes and writes `.note.gnu.build-id`, and either delegates DWARF section creation to `jit_add_debug_info` or calls `elf_update` directly. Cleanup always calls `elf_end` and frees the symbol string table.

## State and Persistence Behavior

The output ELF persists on the provided fd. Most state is local, but `symtab[1]` and global `bnote` are mutated per call, making concurrent calls unsafe without external serialization. Build IDs are deterministic over code, symbol table, and symbol string data.

## Dependencies and Integration Points

It depends on libelf, BLAKE2s, `genelf.h` architecture macros, jitdump format definitions, optional libdw/DWARF support, and Linux alignment/compiler helpers. Perf uses the generated ELF so later symbolization/debug lookup can treat JIT code like a normal DSO.

## Risks and Edge Cases

Section indexes and `sh_link` values differ depending on optional unwind/debug sections and are easy to break. Pointer arithmetic on `void *` relies on compiler extensions. Build ID excludes unwind/debug data, so two files with same code/symbols but different debug data share a build ID. Global mutable `symtab`/`bnote` can race. Error paths use warnings but return only `-1`.

## Test Signals

Tests should generate ELF files with code only, with unwind data, with debug entries, and with both optional features; inspect them with `readelf`, verify executable `.text`, symbol table, build ID determinism, section links, unwind section addresses, and perf symbolization of JIT samples.
