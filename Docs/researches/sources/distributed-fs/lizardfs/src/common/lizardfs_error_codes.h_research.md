<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.h -->
# sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.h

## Purpose
Defines the canonical wire/status error code enum for LizardFS operations. The source was read completely for this report.

## Important APIs, Types, And Functions
`enum lizardfs_error_code` lists status 0 plus protocol, filesystem, chunk, lock, metadata, and POSIX-like errors through `LIZARDFS_ERROR_MAX`; declares `lizardfs_error_string`.

## Control Flow
No runtime flow in the header.

## State And Persistence Behavior
Values are protocol ABI and may be persisted or sent over the network.

## Dependencies And Integration Points
Consumed by `mfserr.cc`, protocol handlers, and clients; includes `<stdint.h>` for C-compatible code.

## Risks And Edge Cases
Renumbering or reusing codes breaks wire compatibility. New codes must be added consistently across string and errno conversion tables.

## Test Signals
Compile coverage plus explicit ABI/value tests are recommended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.h -->
