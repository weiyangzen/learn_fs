# sources/compression/zlib/watcom/watcom_l.mak

`watcom_l.mak` builds zlib for OpenWatcom large-model DOS targets. It mirrors the flat-model makefile but uses `CC=wcc`, `LINKER=wcl`, `-ml` large-model flags, and outputs `zlib_l.lib`.

The default target builds the static library and links `example.exe` and `minigzip.exe`. `wlib` archives the same core zlib object list, while the `.C.OBJ` rule compiles with DOS target, optimization, and warnings-as-errors settings.

Persistent state is local build artifacts: `.obj`, `zlib_l.lib`, and executables. Integration touches legacy large-model behavior described by `zconf.h`, including far pointers and allocation limits. Risks include source-list drift, stale objects due to no dependency files, pointer/allocation assumptions in large model, and cleanup leaving executables. Successful OpenWatcom build and execution of examples are the key test signals.
