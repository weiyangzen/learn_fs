# sources/distributed-fs/openafs/src/tools/dumpscan/dumpfmt.h

Purpose: central description of AFS volume dump wire-format constants and embedded AFS directory page layouts.

Important definitions: dump version and begin/end magic values; top-level tags for dump header, volume header, vnode, and dump end; attribute tags for dump headers, volume headers, and vnodes; directory constants `AFS_DIR_MAGIC`, entries per page, max pages, and hash bucket count. It defines packed-format structs `afs_dir_pagehdr`, `afs_dir_header`, `afs_dir_direntry`, and union `afs_dir_page`.

State/dependencies: this header defines format, not behavior. It depends on `intNN.h` for sized AFS integer aliases.

Integration points: all parser/writer files use these tag constants to keep read/write symmetry. `directory.c` and `repair.c` use the directory page structures when interpreting or generating directory data.

Risks/test signals: these structs assume the OpenAFS dump/on-disk directory layout and alignment remain compatible with the C representation. Any tag mismatch causes parser desynchronization, so round-trip tests through `ParseDumpFile` and `Dump*` are key.
