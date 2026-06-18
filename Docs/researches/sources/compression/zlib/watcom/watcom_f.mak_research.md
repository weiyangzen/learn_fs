# sources/compression/zlib/watcom/watcom_f.mak

`watcom_f.mak` builds zlib for OpenWatcom flat-model DOS targets. It compiles the zlib C source set, archives `zlib_f.lib`, and links `example.exe` and `minigzip.exe`.

The makefile defines `CC=wcc386`, `LINKER=wcl386`, flat-model CFLAGS including `-mf`, DOS target flags, optimization, and warnings-as-errors. The `.C.OBJ` rule compiles sources; `wlib` adds objects to the static library; executable targets link against that library, with `example.exe` using `-ldos32a`.

State is generated `.obj`, `zlib_f.lib`, and executables in the working directory. `clean` removes objects and the library but not the executables. Integration is specific to OpenWatcom `wmake` syntax and the zlib source list. Risks include source-list drift, nonportable syntax, warnings-as-errors on legacy compilers, and incomplete cleanup. Test signals are successful `wmake -f watcom_f.mak` and working example utilities.
