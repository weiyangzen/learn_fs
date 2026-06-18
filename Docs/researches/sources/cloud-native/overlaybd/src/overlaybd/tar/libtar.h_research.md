# sources/cloud-native/overlaybd/src/overlaybd/tar/libtar.h

Purpose: public declarations and constants for Overlaybd's libtar-derived parser and extractor.

Important APIs/types/functions: tar constants define block size, name/prefix lengths, filesystem block size, GNU long header types, PAX keys, and option flags. `TarHeader` maps the POSIX ustar header and exposes metadata/checksum helpers. `PaxHeader` owns parsed PAX overrides and raw records. `TarCore` wraps a source `IFile`, current header, parser options, PAX state, and pathname/linkname helpers. `UnTar` extends `TarCore` with extraction into a target `IFileSystem`, optional base file, meta-only mode, tar-index replay mode, xattr filesystem pointer, unpacked path set, and deferred directory time list.

Control flow: callers instantiate `UnTar` or `TarCore`, call `read_header` to advance, inspect `header` and helper getters, or call `extract_all` / `dump_tar_headers`. `UnTar` private methods implement per-type extraction and whiteout handling.

State and persistence: `TarCore` owns transient parser state for a single stream. `UnTar` owns mutable extraction bookkeeping and writes persistent filesystem objects or LSMT mappings. PAX objects free allocated buffers in destructors; `TarHeader` long name/link pointers are freed by `TarCore` reset/destruction.

Dependencies/integration: included by `header.cpp`, `libtar.cpp`, `whiteout.cpp`, `tar_file.cpp`, tar tests, and EROFS code paths. Depends on Photon `IFile`, `IFileSystem`, `IFileSystemXAttr`, fiemap, tar/POSIX headers, and STL containers.

Risks: helper functions are `static` in the header, so each translation unit gets its own copy. The `libtar_version` variable is defined in the header, which can create multiple definitions if included in multiple linked objects without compiler/linker tolerance. Raw owning pointers and manual allocation require careful reset ordering. Macros for file type detection combine tar typeflag and mode in ways that may classify unusual malformed headers.

Test signals: exercised through tar unit/integration tests and EROFS tests; no direct header-only tests beyond compile and consumers.
