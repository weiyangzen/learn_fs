# sources/distributed-fs/orangefs/src/io/description/pint-distribution.h

## Purpose
Defines the OrangeFS internal distribution abstraction, its method table, packed-size and encode/decode macros, and registry/copy APIs.

## Important APIs, Types, And Functions
Defines `PINT_DIST_NAME_SZ`, `PINT_dist_methods`, `PINT_dist`, `PINT_DIST_PACK_SIZE`, `encode_PINT_dist`, `decode_PINT_dist`, and prototypes for create/free/copy/getparams/setparams/lookup/encode/decode/dump/register/unregister.

## Control Flow
Consumers create or decode a `PINT_dist`, then call its method table for offset mapping, contiguous length, logical file size, data-file count, parameter setting, block size, parameter encode/decode, and lifecycle hooks.

## State And Persistence
Defines packed distribution layout: structure, rounded name bytes, and rounded parameter bytes in one allocation. Decode allocates a packed object and fixes internal pointers. Persistent encoded form contains distribution name and parameter payload, not function pointers.

## Dependencies And Integration Points
Includes `pint-request.h` for `PINT_request_file_data` and PVFS types. Distribution implementations populate `PINT_dist_methods`; request encoding and metadata storage use the encode/decode macros.

## Risks And Test Signals
Risks include macros that call `exit(1)` on decode/encode method lookup failure, pointer fix-up complexity, and reliance on distribution registry being initialized before decode. Tests should verify packed-size layout, encode/decode for every built-in distribution, and behavior for unknown distribution names.
