# sources/compression/zlib/contrib/minizip/zip.h

## Purpose
`zip.h` is the public MiniZip writer header. It declares archive creation, entry creation, entry writing, archive closing, duplicate checking, and extra-field helper APIs.

## Important APIs, Types, and Functions
- Opaque handle `zipFile`, optionally strict-typed under `STRICTZIP` or `STRICTZIPUNZIP`.
- Status constants: `ZIP_OK`, `ZIP_EOF`, `ZIP_ERRNO`, `ZIP_PARAMERROR`, `ZIP_BADZIPFILE`, and `ZIP_INTERNALERROR`.
- `tm_zip` and `zip_fileinfo` describe entry timestamps and attributes.
- Append modes: `APPEND_STATUS_CREATE`, `APPEND_STATUS_CREATEAFTER`, and `APPEND_STATUS_ADDINZIP`.
- API families include `zipOpen*()`, `zipOpenNewFileInZip*()`, `zipWriteInFileInZip()`, `zipCloseFileInZip*()`, `zipAlreadyThere()`, `zipClose()`, and `zipRemoveExtraInfoBlock()`.

## Control Flow
The header describes the normal write sequence: open an archive, open each entry with desired metadata/compression/raw/encryption/Zip64 settings, write entry bytes, close the entry, and close the archive with an optional global comment.

## State and Persistence
State is hidden behind `zipFile` and implemented in `zip.c`. Caller-visible structures carry per-entry metadata into the writer.

## Dependencies and Integration Points
Includes zlib and MiniZip IO callback declarations, and optionally bzip2 declarations. It is consumed by `minizip.c`, package tests, and external applications.

## Risks and Edge Cases
Many compatibility wrappers expose overlapping parameter sets; callers must choose the Zip64-aware variants for large files. Raw mode and encryption have strict preconditions documented only in comments. The 32-bit close API can truncate raw uncompressed sizes. `zipAlreadyThere()` is declared as a convenience but returns non-standard negative values for invalid central directory and memory failure.

## Test Signals
Compilation of sample utilities validates the declarations. Runtime coverage comes from `minizip` round-trip tests and any downstream package tests that build sample consumers.
