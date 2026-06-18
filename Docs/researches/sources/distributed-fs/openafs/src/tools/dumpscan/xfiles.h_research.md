# sources/distributed-fs/openafs/src/tools/dumpscan/xfiles.h

## Purpose
Defines the `XFILE` type and declares the extensible file-like API used by dumpscan. It is the public contract shared by concrete xfile backends and dump parser code.

## Important APIs, Types, And Functions
The central type is `struct XFILE`, with backend callbacks for read, write, tell, seek, skip, and close; counted `dt_uint64 filepos`; capability flags; passthrough target; and backend `refcon`. The header declares openers for generic `xfopen`, path, `FILE *`, fd, Rx call, vol dump, and profile streams, registration via `xfregister`, and standard operations including `xfprintf`/`vxfprintf`.

## Control Flow
Consumers initialize an `XFILE` through one of the open functions, use standard operations for I/O and positioning, optionally install a passthrough stream, and release resources with `xfclose`. Backend implementers fill callback fields and capability flags to opt into seek, skip, write, and close behavior.

## State And Persistence
The header owns no state. It defines where per-stream runtime state and backend-specific pointers are stored. Persistent effects depend entirely on the backend implementation referenced by the callback table.

## Dependencies And Integration Points
It includes stdio, varargs, and dumpscan integer definitions from `intNN.h`, and forward-declares Rx call/connection types to avoid forcing Rx headers on all users. It connects all dumpscan parser and xfile backend modules.

## Risks And Test Signals
Because `XFILE` is a manual vtable, risks are uninitialized callbacks, mismatched capability flags, backend lifetime bugs in `refcon`, and ABI drift if fields are reordered. Compile coverage for all xfile backends and runtime tests for open/read/write/seek/close paths are the main signals.
