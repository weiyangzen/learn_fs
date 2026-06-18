# sources/compression/zlib/contrib/minizip/mztools.c

## Purpose
`mztools.c` provides an auxiliary recovery routine, `unzRepair()`, that rebuilds a ZIP central directory from local file headers when the original central directory is missing or damaged.

## Important APIs, Types, and Functions
- Exports `unzRepair(const char *file, const char *fileOut, const char *fileOutTmp, uLong *nRecovered, uLong *bytesRecovered)`.
- Uses local little-endian access macros `READ_8/16/32` and `WRITE_8/16/32`.
- Reads local file header signature `0x04034b50`, writes central directory header `0x02014b50`, and writes end-of-central-directory signature `0x06054b50`.

## Control Flow
The function opens the input ZIP, repaired output, and temporary central-directory output. It scans 30-byte local headers from the input. For each valid local file header it copies the local header, filename, extra field, and compressed data to the repaired output, synthesizes a matching central directory entry into the temporary file, and increments entry and byte counters. Once scanning stops, it writes a final end-of-central-directory record to the temporary file, appends the temporary central directory to the repaired output, closes streams, deletes the temporary file, and returns recovered counts on success.

## State and Persistence
Persistent effects are `fileOut` and the transient `fileOutTmp`. In-memory state includes running output offsets, central-directory offset, recovered entry count, total recovered bytes, fixed filename/extra buffers, and parsed header fields.

## Dependencies and Integration Points
Depends on zlib status codes and `uLong`, includes `unzip.h`, but performs raw `FILE *` IO rather than using `unzFile` callbacks. It is declared in `mztools.h` for consumers that need repair functionality.

## Risks and Edge Cases
The routine only understands classic local headers with 32-bit sizes and does not handle data descriptors, Zip64 extra sizes, multi-disk archives, encryption headers, or very large filename/extra fields beyond 1024 bytes. It trusts local header compressed-size fields for allocation and copying, which can consume large memory or fail on corrupted sizes. It writes central directory offsets and sizes using 32-bit fields, clipping entries above `0xffff`.

## Test Signals
No direct test appears in this subset. Meaningful tests would feed truncated archives with known local headers and verify recovered entry count, output readability, and failure behavior on data-descriptor and Zip64 archives.
