# sources/compression/zlib/contrib/minizip/mztools.h

## Purpose
`mztools.h` declares the MiniZip repair helper API exposed by `mztools.c`.

## Important APIs, Types, and Functions
The public API is `unzRepair()`, exported with `ZEXPORT`. It accepts an input ZIP path, repaired output path, temporary central-directory path, and optional output counters for recovered entries and recovered bytes.

## Control Flow
This header has no runtime control flow. It sets an include guard, provides C++ `extern "C"` linkage, includes `zlib.h` when needed, includes `unzip.h`, and declares the repair function.

## State and Persistence
No state is stored in the header. The declared function persists output files when called.

## Dependencies and Integration Points
Consumers include this header alongside MiniZip headers. It depends on `uLong` from zlib and the MiniZip unzip declarations for package context.

## Risks and Edge Cases
The API contract mentions a temporary filename but does not define cleanup semantics on all failure modes; implementation removes the temp file after the merge path. Because the declaration uses filesystem paths rather than MiniZip IO callbacks, alternate IO backends cannot use it directly.

## Test Signals
There are no direct header tests. Compilation of a consumer including `mztools.h` validates linkage declarations; functional testing belongs to `unzRepair()`.
