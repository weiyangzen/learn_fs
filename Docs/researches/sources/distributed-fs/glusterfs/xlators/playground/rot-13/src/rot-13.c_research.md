# sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/rot-13.c

## Purpose
Implements a demonstration translator that applies ROT13 to write buffers before sending them to disk and applies ROT13 again to read buffers before returning to the caller. The file explicitly marks the translator as an example, not production code.

## Important APIs, Types, And Functions
`rot13()` transforms alphabetic bytes in place. `rot13_iovec()` applies it to each iovec. `rot13_readv()` winds child readv and `rot13_readv_cbk()` optionally decrypts returned vectors. `rot13_writev()` optionally encrypts user vectors before winding child writev. `init()` validates exactly one child, parses `encrypt-write` and `decrypt-read`, allocates `rot_13_private_t`, and sets defaults to enabled. `fini()` frees private state. The fop table exposes only readv and writev.

## Control Flow
Reads pass through to the child and are transformed in the callback immediately before unwind. Writes are transformed before the child sees the buffers. Init stores booleans from translator options, with errors for non-boolean values.

## State And Persistence
Persistent translator state is just two booleans in `rot_13_private_t`. Data persistence is external: if `encrypt-write` is enabled, bytes stored below this translator are ROT13-encoded.

## Dependencies And Integration Points
Uses Gluster xlator/frame APIs, logging, dict options, and the `rot-13.h` private struct. It requires one child and supports no cbks beyond the default empty struct.

## Risks
It mutates input and output iovec memory in place, which can surprise callers or violate ownership expectations in real stacks. It has minimal validation, no memory accounting, no xlator_api object, and no handling for partial writes, checksums, metadata, direct I/O, or binary-safe encryption semantics. ROT13 is not encryption.

## Test Signals
A round-trip write/read of alphabetic text should return original data when both options are on, stored data should be transformed under the translator, and disabling either option should produce one-way transformed behavior. Binary and shared-buffer tests would expose the in-place mutation risk.
