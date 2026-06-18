# sources/distributed-fs/coda/coda-src/dir/coda_dir.h

## Purpose
Legacy public directory and buffer interface, mostly exposing old AFS-style directory operations over `long *` file identifiers.

## APIs, Types, and Functions
Declares directory operations `NameBlobs()`, `Create()`, `Delete()`, `MakeDir()`, `Lookup()`, `GetBlob()`, `DirHash()`, `EnumerateDir()`, `DirToNetBuf()`, `FindName()`, `IsEmpty()`, and `Length()`. It defines `struct buffer` and declares buffer-cache routines `DInit()`, `DRead()`, `DRelease()`, `DFlush()`, `DNew()`, `DZap()`, plus salvage APIs `DirOK()` and `DirSalvage()`.

## Control Flow, State, and Persistence
No implementation in this header. The API implies page-buffered persistent directory files addressed by a five-int cache key and page number, with dirty/locker fields for cache state.

## Dependencies and Integration
Used by old salvage code and tests. Newer code primarily uses `codadir.h`/`dirbody.h`, so this header is a compatibility bridge.

## Risks and Test Signals
Risks include K&R-era prototypes, `long *` untyped identifiers, platform-specific `buffer` typedef, and stale declarations that may no longer match modern implementations. Test signals are legacy salvage/test compilation and correct buffer-cache behavior where still linked.
