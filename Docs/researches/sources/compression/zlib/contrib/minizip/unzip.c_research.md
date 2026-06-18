# sources/compression/zlib/contrib/minizip/unzip.c

## Purpose
`unzip.c` implements the MiniZip read API for listing ZIP central directories, locating entries, opening the current entry, reading stored/deflated/bzip2 data, optional classic decryption, Zip64 metadata handling, and offset/comment utilities.

## Important APIs, Types, and Functions
- Public open/close and metadata APIs: `unzOpen()`, `unzOpen64()`, `unzOpen2()`, `unzOpen2_64()`, `unzClose()`, `unzGetGlobalInfo()`, `unzGetGlobalInfo64()`, `unzGetGlobalComment()`.
- Directory navigation APIs: `unzGoToFirstFile()`, `unzGoToNextFile()`, `unzLocateFile()`, `unzGetFilePos64()`, `unzGoToFilePos64()`, `unzGetOffset64()`, `unzSetOffset64()`.
- Entry metadata APIs: `unzGetCurrentFileInfo()` and `unzGetCurrentFileInfo64()`.
- Entry read APIs: `unzOpenCurrentFile3()`, compatibility wrappers, `unzReadCurrentFile()`, `unztell64()`, `unzeof()`, `unzGetLocalExtrafield()`, and `unzCloseCurrentFile()`.
- Internal state types: `unz64_s`, `unz_file_info64_internal`, and `file_in_zip64_read_info_s`.

## Control Flow
Opening a ZIP fills IO callbacks, opens the file, searches backwards for a Zip64 EOCD locator first and classic EOCD second, parses central-directory counts and offsets, rejects multi-disk archives, computes `byte_before_the_zipfile` for self-extracting prefixes, allocates `unz64_s`, and positions on the first central-directory entry. Navigation advances `pos_in_central_dir` by fixed header plus variable name/extra/comment lengths. Current-file info parsing reads a central header, optional filename/extra/comment buffers, and Zip64 extra field overrides. Opening an entry checks the local header against central metadata, allocates a read buffer, initializes inflate or bzip2 state when needed, handles password setup, and stores compressed/uncompressed counters. Reading refills compressed input from the archive, decrypts if needed, then either copies stored/raw bytes or inflates/decompresses into the caller buffer while updating CRC and counters. Closing an entry validates CRC when fully read and frees decompressor state.

## State and Persistence
All runtime state is held in the `unz64_s` handle and, when an entry is open, `file_in_zip64_read_info_s`. It tracks archive-level central directory position, current entry metadata, open entry read stream, CRC progress, remaining compressed/uncompressed bytes, decryption keys, and Zip64 status. The reader does not mutate the archive.

## Dependencies and Integration Points
Uses zlib inflate and CRC APIs, MiniZip `ioapi.h` callbacks, optional bzip2 when `HAVE_BZIP2` is enabled, and optional Info-ZIP classic crypto through `crypt.h` unless `NOUNCRYPT` is defined. The public declarations are in `unzip.h`; command-line `miniunzip` and tests consume this API.

## Risks and Edge Cases
Multi-disk ZIP files are unsupported. Some 32-bit compatibility APIs truncate 64-bit sizes and offsets. Bzip2 entries become raw reads when compiled without bzip2 support in one path, which can surprise callers. Password verification only consumes the classic 12-byte encryption header and does not provide modern encryption. `unzLocateFile()` rejects search names at or above `UNZ_MAXFILENAMEINZIP`, and central-directory parsing assumes structurally valid variable-length fields.

## Test Signals
MiniZip round-trip CTest cases indirectly exercise opening, first-file navigation, reading, CRC validation, and extraction. The subset lacks direct tests for Zip64, bzip2, encrypted entries, local extra field reads, random access offsets, malformed central directories, and CRC error reporting.
