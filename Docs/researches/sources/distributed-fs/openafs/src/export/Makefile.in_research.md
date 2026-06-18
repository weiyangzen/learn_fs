# sources/distributed-fs/openafs/src/export/Makefile.in

This AIX-focused Makefile builds and installs the OpenAFS EXPORT kernel extension, export lists, and loader/configuration helpers. It generates 32-bit and 64-bit export files from AIX-version-specific `.exp` inputs, compiles `export.c`/`symtab.c` variants, links `export.ext` and `.nonfs` extensions, and builds `cfgexport`/`cfgafs` helper binaries.

Control flow is heavily conditional on `SYS_NAME`, `AIX32`, and `AIX64`. AIX 4/5/6/7 branches choose compile flags such as `__XCOFF64__`, `AFS_64BIT_KERNEL`, `AFS_AIX51_ENV`, and kernel options. Install/dest targets stage kernel modules, config helpers, and export maps to kernel and client/server destination trees. State includes generated export maps, kernel extension objects, helpers, and installed files.

Dependencies are AIX `ld`, XCOFF, kernel export/import files, OpenAFS make fragments, and `extras.exp`. Integration is AIX kernel module loading and symbol import for OpenAFS. Risks are platform-specific fragility, duplicated targets, stale AIX export lists, and 32/64-bit divergence. Test signals are AIX builds for enabled widths, load/unload of `export.ext`, and successful OpenAFS kernel extension import of missing symbols.
