# sources/distributed-fs/openafs/src/WINNT/client_config/cellservdb.h

## Purpose
`cellservdb.h` defines the C ABI, data model, constants, and prototypes for the CellServDB editor used by the Windows configuration tool.

## Important APIs, Types, and Functions
It defines `BOOL` fallback values, `MAX_CSDB_PATH`, `cchCELLDBLINE`, linked-list node `CELLDBLINE`, owner `CELLSERVDB`, and parsed record `CELLDBLINEINFO`. Prototypes cover file discovery/read/write/free, line parse/format, cell lookup, cell/server removal, and cell/server/line insertion.

## Control Flow
The header exposes a list-oriented workflow: call `CSDB_ReadFile`, inspect or modify linked nodes through `CSDB_*` helpers, call `CSDB_WriteFile`, then call `CSDB_FreeFile`. C++ consumers include it under `extern "C"` guards.

## State and Persistence Behavior
`CELLSERVDB` carries all mutable state: `szFilename`, `fChanged`, and list head/tail. Each `CELLDBLINE` owns one fixed-size raw text line plus previous/next links. `CELLDBLINEINFO` is a parsed transient representation.

## Dependencies and Integration Points
The header is included by `afs_config.h`, `tab_hosts.cpp`, and validation paths in `tab_general.cpp`. It is intentionally C-compatible so both `.c` and `.cpp` sources can share the same parser.

## Risks and Edge Cases
The local `BOOL` typedef can conflict if included after Win32 headers in a C file. Fixed 512-byte line buffers and 2048-byte path buffers constrain long CellServDB entries. Callers must not mutate linked-list pointers directly because the implementation depends on them for file order.

## Test Signals
ABI checks should compile both C and C++ consumers. Functional tests should use the public sequence read, find, add/remove, write, free, and should validate behavior when lines exceed `cchCELLDBLINE`.
