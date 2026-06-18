# sources/distributed-fs/openafs/src/WINNT/license/multistring.cpp

## Purpose

`multistring.cpp` implements a small TCHAR multistring helper used by the license converter. It supports allocation, freeing, walking, length/count calculation, case-insensitive search, append, and delete over strings separated by an arbitrary separator character, including `'\0'` for conventional double-null multistrings.

## Important APIs, types, and functions

`lstrncmpi` is a local case-insensitive bounded comparison using `CharNext` and `toupper`. Public functions are `mstralloc`, `mstrfree`, `mstrwalk`, `mstrlen`, `mstrcount`, `mstrstr`, `mstrcat`, and `mstrdel`.

## Control flow

`mstrwalk` is the iterator primitive. On first call, when `*ppSegment` is null, it returns the first segment; on later calls it advances by the previous segment length, consumes the separator, and returns the next segment until it reaches an empty segment. `mstrlen`, `mstrcount`, and `mstrstr` are simple loops over `mstrwalk`.

`mstrcat` computes the old multistring length, the appended string length, and how many characters to retain before the terminal separator. It allocates a new buffer, copies retained content, inserts a separator when needed, copies the appended string, double-terminates when `chSep` is null, frees the old buffer, and updates the caller's pointer. `mstrdel` allocates a replacement buffer and copies all segments except case-insensitive exact matches for the removal string.

## State and persistence behavior

All multistring memory is allocated with `GlobalAlloc(GMEM_FIXED)` and must be released with `mstrfree`. The functions mutate the caller's pointer on append/delete and do not persist state elsewhere.

## Dependencies and integration points

The implementation depends on `windows.h`, TCHAR APIs, `GlobalAlloc`, `GlobalFree`, `lstrlen`, `lstrcpy`, `CharNext`, and CRT `toupper`. `main.cpp` uses `mstrcat` to collect wildcard-expanded filenames and `mstrfree` after translation.

## Risks and edge cases

`lstrncmpi` calls `toupper` on `TCHAR`, which is not correct for Unicode builds with wide characters. `mstrcat` does not validate `pszAppend` before `lstrcpy`; null append computes zero length but can still dereference null. The helpers repeatedly allocate and copy on every append, so large file lists scale poorly. Separator handling is subtle when `chSep` is null versus non-null, and callers must initialize the pointer to null.

## Test signals

Tests should cover appending to null and non-empty multistrings, walking null-separated and comma-separated variants, deleting first/middle/last/all entries, case-insensitive matching, Unicode/TCHAR build behavior, null append handling, and length/count consistency.
