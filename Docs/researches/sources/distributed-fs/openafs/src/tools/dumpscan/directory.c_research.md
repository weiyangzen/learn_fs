# sources/distributed-fs/openafs/src/tools/dumpscan/directory.c

Purpose: parses, searches, and generates AFS directory data in on-disk/dump page format.

Important APIs/functions: `parse_directory` reads 2 KiB pages, checks the `AFS_DIR_MAGIC` tag, walks allocated directory entries, prints when `DSPRINT_DIR` is set, and invokes `cb_dirent`. `ParseDirectory` is the public wrapper. `DirectoryLookup` installs a temporary `cb_dirent` to search by name or vnode. Generation functions `Dir_Init`, `Dir_AddEntry`, `Dir_Finalize`, `Dir_EmitData`, and `Dir_Free` build directory pages with hash chains and allocation bitmaps.

State/persistence: parser state is transient except callback side effects. Generator state lives in `struct dir_state` until emitted to an `XFILE`, optionally with a `VTAG_DATA` tag. Dependencies include `afs/dir.h`, `dumpfmt.h`, byte-order conversion, `XFILE`, and parser error callbacks.

Risks/test signals: the parser trusts many on-disk sizes and name layouts after basic checks; corrupted allocation bitmaps can skip entries or abort pages. Generation has a 128-page old-style allocation map assumption. Test signals are directory listings, lookup success, and downstream path building/extraction behavior.
