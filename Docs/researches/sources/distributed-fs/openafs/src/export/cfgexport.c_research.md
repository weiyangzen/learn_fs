# sources/distributed-fs/openafs/src/export/cfgexport.c

This AIX userspace helper loads/configures the EXPORT kernel extension and passes it a translated kernel symbol table. It accepts `-a mod_file`, `-d mod_file`, optional `-s symbols` defaulting to `/unix`, and debug `-Z`. It persists kmid in `<mod_file>.kmid`.

Important functions are `get_syms`, `xlate_xtok`, `find_suffix`, `xsym_compar`, `dump_xsym`, `dump_ksym`, `error`, and `sys_error`. `get_syms` reads the XCOFF header, symbol table, and string table, filters external/hidden external symbols without strange names, skips aux entries, sorts symbols, uniquifies them, translates to EXPORT `sym_t` records, and fills `struct k_conf`. `xlate_xtok` builds a compact string table using suffix sharing, with 64-bit and 32-bit XCOFF handling. `main` loads the kernel module and passes `k_conf` through `SYS_CFGKMOD`.

State is allocated symbol/string tables, loaded module state, and kmid file persistence. Dependencies are AIX XCOFF, sysconfig, ldr, `export.h`, and `sym.h`. Risks include fixed `SYMBUFSIZE` behavior in 64-bit code, unchecked integer sizes, path buffer overflow, old-style varargs declarations, and symbol-table parsing fragility. Test signals are debug dumps, load/configure/unload cycles, and symbol lookup success from the kernel extension.
