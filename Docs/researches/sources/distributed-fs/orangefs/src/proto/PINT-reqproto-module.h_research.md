<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-module.h -->
# sources/distributed-fs/orangefs/src/proto/PINT-reqproto-module.h

## Purpose
Defines the internal plugin interface for protocol encoding modules. It abstracts concrete encoders behind function pointers and describes the generic message header shared by all encoded buffers.

## Important APIs, Types, and Functions
Defines `PINT_encoding_functions` with request/response encode, request/response decode, encode/decode release, and max-size callbacks. Defines `PINT_ENC_GENERIC_HEADER_SIZE` as 8 bytes and `PINT_encoding_table_values`, which carries the function table, module name, init/finalize hooks, generic header storage, and numeric encoding type. Declares external `le_bytefield_table`.

## Control Flow
The dispatcher initializes module table entries, calls each module's init/finalize functions, uses `generic_header` as the prefix copied into encoded buffers, and calls the operation callbacks based on encoding type and message direction.

## State and Persistence
No standalone state is stored here. Concrete modules provide global table values whose header bytes and `enc_type` are initialized at runtime.

## Dependencies and Integration Points
Consumed by `PINT-reqproto-encode.c` and implemented by `PINT-le-bytefield.c`. It depends on request/response structs, `PINT_encoded_msg`, `PINT_decoded_msg`, `PVFS_BMI_addr_t`, and `PVFS_server_op` being visible to compilation units that include it.

## Risks
The interface has no version field beyond the generic header populated elsewhere. Callback implementations must agree on buffer ownership and release semantics. Adding another encoding requires increasing or fitting within the dispatch table size in `PINT-reqproto-encode.c`.

## Test Signals
Compile a module against the interface, initialize and dispatch through `PINT_encoding_table_values`, verify the 8-byte header layout, and check release callback behavior for failed partial encodes/decodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-module.h -->
