# sources/distributed-fs/openafs/src/tools/dumpscan/pathname.c

Purpose: builds a vnode hash table from a dump and uses it to resolve volume-relative paths or construct paths for vnodes.

Important APIs/functions: `Path_PreScan` runs a secondary `dump_parser` over the dump, collecting volume file count, vnode offsets, parent links, directory data offsets/sizes, and directory-entry parent relationships. `Path_Follow` tokenizes a path, repeatedly seeks to parent directory data, and calls `DirectoryLookup` by name. `Path_Build` walks parent links from a vnode to root, either using fast numeric components or reverse directory lookups for real names. `Path_FreeHashTable` releases entries.

State/dependencies: persistent state is `path_hashinfo.hash_table`, sized from volume file count. It depends on seekable `XFILE`s, `DirectoryLookup`, parser callbacks, and accurate directory vnode data.

Risks/test signals: `Path_Follow` mutates its input string with `strtok` and appears to call `strtok(path, "/")` twice, skipping the first component. Missing parents or incomplete directory data are fatal. Strong signals are successful `afsdump_scan -Pp` and path-based extraction.
