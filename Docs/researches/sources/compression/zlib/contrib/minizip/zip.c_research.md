# sources/compression/zlib/contrib/minizip/zip.c

## Purpose
`zip.c` implements the MiniZip writer API for creating, appending to, and closing ZIP archives, including local and central header generation, Zip64 support, optional bzip2 compression, optional classic encryption, duplicate-name detection, and extra-field cleanup.

## Important APIs, Types, and Functions
- Public open APIs: `zipOpen()`, `zipOpen64()`, `zipOpen2()`, `zipOpen2_64()`, and `zipOpen3()`.
- Entry APIs: `zipOpenNewFileInZip4_64()` as the main implementation, compatibility wrappers down to `zipOpenNewFileInZip()`, `zipWriteInFileInZip()`, `zipCloseFileInZipRaw64()`, and `zipCloseFileInZip()`.
- Archive close and utilities: `zipClose()`, `zipAlreadyThere()`, and `zipRemoveExtraInfoBlock()`.
- Internal state types: `zip64_internal`, `curfile64_info`, central-directory `linkedlist_data`, skipset `set_t`, and `block_t`.
- Internal writers/parsers handle little-endian values, EOCD search, Zip64 EOCD emission, local-header patching, UTF-8 flag detection, and central directory caching.

## Control Flow
`zipOpen3()` initializes IO callbacks, opens or creates the archive, optionally loads an existing central directory for append mode, and prepares linked-list storage. Opening a new entry closes any already-open entry, validates method/field lengths, sets flags for compression level, encryption, and UTF-8 names, builds an in-memory central header, writes the local header with placeholder CRC/sizes, initializes deflate or bzip2 state, and writes an encryption header when needed. `zipWriteInFileInZip()` updates CRC and either compresses into an internal buffer or copies stored/raw input, flushing buffered compressed bytes to the output stream. Closing an entry finishes compression, flushes pending bytes, ends compressor state, computes final sizes, patches central header fields, adds Zip64 extra data when thresholds require it, patches the local header or local Zip64 extra field, appends the central header to the linked-list directory, and advances entry count. `zipClose()` writes the accumulated central directory, emits Zip64 EOCD records if entry count or offsets overflow classic fields, writes the classic EOCD and global comment, closes the stream, and frees state.

## State and Persistence
Persistent output is the ZIP archive, possibly appended to an existing file. `zip64_internal` tracks the open file stream, central-directory blocks, current open entry, beginning offset for self-extracting prefixes, append offset adjustments, entry count, optional previous global comment, and a lazily built skipset for name lookups. `curfile64_info` tracks compressor streams, local header position, central header buffer, flags, CRC, encryption state, Zip64 offsets, and compressed/uncompressed totals.

## Dependencies and Integration Points
Uses zlib deflate/CRC, MiniZip `ioapi.h` callbacks, optional bzip2 compression, optional `crypt.h`, and `skipset.h`. Public declarations live in `zip.h`; `minizip.c` exercises this API. Append mode reads existing central directories using internal EOCD parsers compatible with `unzip.c` concepts.

## Risks and Edge Cases
Multi-disk ZIP files are unsupported. Raw mode requires callers to supply correct CRC and uncompressed size and to strip Zip64 extra blocks when copying entries. `zipRemoveExtraInfoBlock()` reads `short` fields via unaligned casts and assumes well-formed extra data. `zipOpenNewFileInZip4_64()` writes into `central_header` before checking allocation failure, a potential null dereference on allocation failure. Zip64 local extra space must be requested up front via the `zip64` argument, or large sizes become fatal at close. Classic encryption is weak and requires precomputed CRC.

## Test Signals
CTest round-trip cases exercise creating archives through the CLI and reading them back. No direct tests in this subset cover append mode, `zipAlreadyThere()`, Zip64 boundaries, bzip2 compression, encryption, raw copy mode, allocation failure, or malformed extra fields.
