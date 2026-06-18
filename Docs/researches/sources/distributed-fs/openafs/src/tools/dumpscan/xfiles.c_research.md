# sources/distributed-fs/openafs/src/tools/dumpscan/xfiles.c

## Purpose
Provides the generic `XFILE` abstraction used by dumpscan. It centralizes read/write/seek/tell/skip/close dispatch, position accounting, passthrough copying, backend registration, and `TYPE:name` opening.

## Important APIs, Types, And Functions
Core operations are `xfread`, `xfwrite`, `xftell`, `xfseek`, `xfskip`, `xfpass`, `xfunpass`, `xfclose`, `xfregister`, and `xfopen`. Static registration support uses `struct xftype`, `xftypes`, `did_register_defaults`, and `register_default_types`. Default backend openers are declared externally for paths, file descriptors, vol dumps, profile wrappers, and stdio.

## Control Flow
Reads and writes call the backend callbacks, update the counted 64-bit file position, and in the read case optionally pass the bytes through to another writable `XFILE`. Seek/tell prefer backend methods when present, otherwise tell returns the counted position. Skip uses backend skip when available, then absolute seek, and finally a read-and-discard loop, which also preserves passthrough semantics. `xfopen` lazily registers default types, special-cases `-` as stdio, parses an optional `TYPE:` prefix by temporarily NUL-terminating the string, restores the separator, and dispatches to the registered opener.

## State And Persistence
Global state is the backend registry linked list and a boolean noting default registration. Per-stream state lives in each `XFILE`: callback pointers, counted `filepos`, capability flags, passthrough pointer, and backend `refcon`. No filesystem state is owned here, but operations propagate to backend persistence.

## Dependencies And Integration Points
This is the common I/O contract for the dumpscan tree. It depends on `intNN.h` 64-bit helpers, backend files such as `xf_files.c`, `xf_profile.c`, and `xf_rxcall.c`, plus xfile error constants.

## Risks And Test Signals
Risks include no registry synchronization, modification of the caller's open-name buffer during type parsing, no check for duplicate backend names, position drift if a backend performs short reads/writes but reports success, and passthrough write failures causing a read failure after data was consumed. Tests should cover each default backend name, custom registration, colon and non-colon names, passthrough copy and unpass errors, seekless skip fallback, position accounting, and close zeroing.
