# sources/compression/zlib/contrib/minizip/unzip.h

## Purpose
`unzip.h` is the public MiniZip header for ZIP reading. It defines opaque handles, status codes, metadata structures, and function prototypes for archive navigation and entry extraction.

## Important APIs, Types, and Functions
- Opaque handle `unzFile`, optionally strict-typed under `STRICTUNZIP` or `STRICTZIPUNZIP`.
- Status constants: `UNZ_OK`, `UNZ_END_OF_LIST_OF_FILE`, `UNZ_PARAMERROR`, `UNZ_BADZIPFILE`, `UNZ_INTERNALERROR`, and `UNZ_CRCERROR`.
- Metadata structs: `tm_unz`, `unz_global_info`, `unz_global_info64`, `unz_file_info`, `unz_file_info64`, `unz_file_pos`, and `unz64_file_pos`.
- API groups cover open/close, global info/comment, file navigation/location, current file info, open/read/close current entry, tell/eof, local extra field reads, and raw central-directory offsets.

## Control Flow
The header defines the callable surface but no implementation. The intended caller sequence is open archive, inspect global info, navigate or locate an entry, retrieve current-file metadata, open current file, repeatedly read, close current file, and finally close the archive.

## State and Persistence
The caller receives an opaque `unzFile` whose state is implemented in `unzip.c`. Header-defined structures are caller-visible snapshots of archive and entry metadata.

## Dependencies and Integration Points
Includes zlib and MiniZip IO callback declarations. Optionally includes `bzlib.h` when `HAVE_BZIP2` is defined. It is consumed by MiniZip utilities, `mztools`, and external applications embedding MiniZip.

## Risks and Edge Cases
The 32-bit metadata and position APIs can truncate Zip64 values. `unzOpen64()` takes `const void *` to allow wide-character paths through custom callbacks, which weakens type clarity. Compression method constant `Z_BZIP2ED` is exposed even when bzip2 support is optional.

## Test Signals
Compilation of consumers validates declarations. Functional signals come from tests using `miniunzip` and package consumers that include this header.
