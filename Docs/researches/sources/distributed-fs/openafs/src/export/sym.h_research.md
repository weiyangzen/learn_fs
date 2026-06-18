# sources/distributed-fs/openafs/src/export/sym.h

This header defines the simplified symbol-table format used by the AIX EXPORT extension. `struct toc_syment` abstracts the relevant XCOFF symbol value and name/offset fields for 32-bit and 64-bit formats, with macros normalizing access to `n_name`, `n_nptr`, `n_zeroes`, and `n_offset`. It typedefs `sym_t` and declares global `toc_syms`, `toc_nsyms`, and `sym_lookup`.

There is no runtime control flow in the header, but its layout is shared persistent in-memory state between `cfgexport` translation and kernel `export` lookup. Dependencies are XCOFF width macros. Integration is `cfgexport.c`, `export.c`, and `symtab.c`.

Risks are layout drift between userspace-constructed tables and kernel interpretation, especially under `__XCOFF64__`, and macro differences hiding name-storage cases. Test signals are symbol lookup by name and address in both 32-bit and 64-bit builds.
