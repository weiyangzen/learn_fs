<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/modpost.h -->
# sources/distributed-fs/ceph-client/scripts/mod/modpost.h

## Purpose

`modpost.h` defines the shared host-tool ABI for `modpost`, `file2alias`, `sumversion`, and `symsearch`. It abstracts target ELF class/endian handling, unaligned reads, module records, ELF metadata, buffers, aliases, and logging.

## Important APIs, Types, and Functions

Important macros are target-selecting `Elf_*` typedef aliases, `TO_NATIVE()`, `get_unaligned_native()`, `ARRAY_SIZE()`, and `strstarts()`. Important types are `struct buffer`, `struct module_alias`, `struct module`, and `struct elf_info`. Declared functions include `buf_printf()`, `buf_write()`, `symsearch_init()`, `symsearch_find_nearest()`, `handle_moddevtable()`, `get_src_version()`, `read_text_file()`, `get_line()`, `sym_get_data()`, and `modpost_log()`.

## Control Flow

The header has inline helpers for section-index normalization and symbol-name validity. It maps ELF32 or ELF64 types at compile time based on generated `elfconfig.h`, while runtime globals choose endian conversion.

## State and Persistence Behavior

It declares external `target_is_big_endian` and `host_is_big_endian` and structures that own in-memory module lists, alias lists, no-trim symbol data, and parsed ELF pointers. It does not persist files itself.

## Dependencies and Integration Points

It depends on `elfconfig.h`, Linux host helper headers, and `module_symbol.h`. It is included by all module postprocessing translation units.

## Risks and Edge Cases

Type abstraction must match the target object, not the host. Incorrect endian or class configuration corrupts parsing. `get_secindex()` must handle large section tables and reserved ranges consistently. Consumers must free buffers and symsearch state.

## Test Signals

Build `modpost` for ELF32/ELF64 and big/little-endian targets, test more-than-64k sections, mapping symbols, unaligned fields, and error/warn/fatal formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/modpost.h -->
