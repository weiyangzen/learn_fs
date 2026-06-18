# sources/distributed-fs/openafs/src/tools/dumpscan/internal.h

Purpose: private cross-module declarations for dumpscan implementation files.

Important APIs: declares internal parser entry points `parse_volhdr` and `parse_vnode`, directory helper `parse_directory`, backup-header adapter `try_backuphdr`, and utilities `handle_return`, `prep_pi`, and `match_next_vnode`.

State/dependencies: no state. It includes `xfiles.h` and `dumpscan.h`, tying all private declarations to the public parser data model.

Integration points: `parsedump.c` uses `parse_volhdr`, `parse_vnode`, and `try_backuphdr` in its top-level tag table. `parsevnode.c` uses `parse_directory` and `match_next_vnode` for directory callbacks and repair resync. Command-line tools do not include this header directly; it is for library internals.

Risks/test signals: this header exposes non-public symbols without include guards of its own, relying on included headers and compile discipline. Prototype drift would break parser builds. Compile/link of `libdumpscan.a` is the main signal.
