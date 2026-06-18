# sources/distributed-fs/coda/coda-src/dir/salvage.cc

## Purpose
Legacy directory salvager that copies apparently valid entries from a suspect directory into a newly made target directory.

## APIs, Types, and Functions
Implements `DirSalvage(long *fromFile, long *toFile)`. Uses legacy `MakeDir()`, `Delete()`, `DRead()`, `GetBlob()`, `Create()`, and `DRelease()` from `coda_dir.h`/old private directory headers.

## Control Flow, State, and Persistence
The function creates an empty target directory, deletes its `.` and `..`, reads the source first page, estimates used pages by scanning the allocation map, then walks each hash chain. For each in-range entry with a readable blob, it calls `Create()` on the target using the entry name and a pointer-adjusted FID representation, then releases buffers. It returns zero after best-effort copying.

## Dependencies and Integration
Depends on old buffer-cache directory APIs and private layout names. It is not aligned with the newer `codadir.h`/`dirbody.h` API and appears mostly historical.

## Risks and Test Signals
Risks are high: comments call out unsafe pointer arithmetic for FID shape, weak page-validity heuristics, best-effort continuation after errors, and legacy type/layout drift. Test signals are limited to salvaged target readability and retained good entries under the old directory implementation.
