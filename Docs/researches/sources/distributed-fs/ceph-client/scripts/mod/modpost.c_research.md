<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/modpost.c -->
# sources/distributed-fs/ceph-client/scripts/mod/modpost.c

## Purpose

`modpost.c` is the main host-side postprocessor for kernel object metadata. It reads relocatable ELF objects and symbol-version dumps, collects exports and unresolved symbols, checks licenses, namespaces, section mismatches, and module metadata, then writes generated `.mod.c`, `.vmlinux.export.c`, `Module.symvers`, and namespace dependency files.

## Important APIs, Types, and Functions

Key APIs include `read_symbols()`, `parse_elf()`, `handle_symbol()`, `handle_moddevtable()`, `check_sec_ref()`, `extract_crcs_for_object()`, `mod_set_crcs()`, `check_exports()`, `write_mod_c_file()`, `write_vmlinux_export_c_file()`, `read_dump()`, `write_dump()`, `write_namespace_deps_files()`, and `main()`. Core state is held in `struct module`, internal `struct symbol`, the global `modules` list, `symbol_hashtable`, and option flags for module support, modversions, trimming, external modules, warning policy, and endianness.

## Control Flow

`main()` parses options, detects host endian, reads optional symbol dumps, reads object paths from arguments or `-T`, and processes each object. ELF parsing mmaps the object, normalizes endianness, finds sections, symbol tables, `.modinfo`, `.export_symbol`, `.no_trim_symbol`, and initializes nearest-symbol search. Symbol handling records undefined references, exports, init/cleanup presence, module aliases, and metadata. Later passes check section references, license/GPL export use, namespace imports, dependencies, symbol CRCs, module-name length, and generated C output.

## State and Persistence Behavior

In-memory state persists per run across all modules so dependencies can be resolved globally. Persistent outputs include `<module>.mod.c`, `.vmlinux.export.c`, `Module.symvers`-style dumps, and missing namespace dependency files. `write_if_changed()` avoids touching generated files when content is identical.

## Dependencies and Integration Points

It depends on host ELF headers, Kbuild-generated `.mod` and `.*.cmd` files, genksyms `#SYMVER` lines, `license.h`, `file2alias.c`, `sumversion.c`, `symsearch.c`, and kernel list/hash/xalloc helpers. It is central to `make modules`, external module builds, module autoloading, modversion CRCs, namespace enforcement, and section-mismatch diagnostics.

## Risks and Edge Cases

ELF parsing is security-sensitive because malformed object bounds, extended section indices, cross-endian data, and relocation addends are handled manually. Policy flags change warnings into errors. Missing `Module.symvers`, stale `.cmd` files, long symbol names, GPL-only imports by non-GPL modules, namespace drift, and architecture-specific relocation encodings can cause subtle build failures.

## Test Signals

Use `allmodconfig`, `allyesconfig`, external module builds, modversions basic and extended modes, namespace import tests, GPL-only export tests, section-mismatch fixtures, missing-symbol warning/error modes, cross-endian targets, and malformed object tests. Generated `.mod.c` and `Module.symvers` should be stable under no-op rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/modpost.c -->
