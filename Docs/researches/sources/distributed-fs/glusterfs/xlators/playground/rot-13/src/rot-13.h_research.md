# sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/rot-13.h

## Purpose
Declares private configuration state for the sample ROT13 translator.

## Important APIs, Types, And Functions
`rot_13_private_t` contains `encrypt_write` and `decrypt_read` booleans.

## Control Flow
`rot-13.c` reads these flags in read and write paths and initializes them from options.

## State And Persistence
The struct is per-translator in-memory state. It determines whether persisted child data is transformed on writes and whether reads are transformed back.

## Dependencies And Integration Points
Relies on `gf_boolean_t` being available from included Gluster headers in the C file context.

## Risks
The header does not include the Gluster type definition itself, so standalone inclusion without prior Gluster headers would fail.

## Test Signals
Builds including `rot-13.h` after Gluster headers should compile; option toggles should change the two flags.
