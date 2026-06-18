<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.c -->
# sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.c

## Purpose
Provides the public protocol encode/decode dispatcher for OrangeFS request protocol messages. It initializes the supported encoding table, stamps/validates generic protocol headers, dispatches to concrete encoder modules, and releases encoded/decoded resources.

## Important APIs, Types, and Functions
Exports `PINT_encode_initialize`, `PINT_encode_finalize`, `PINT_encode`, `PINT_decode`, `PINT_encode_release`, `PINT_decode_release`, and `PINT_encode_calc_max_size`. Internal state is `PINT_encoding_table[ENCODING_TABLE_SIZE]`. The file currently supports `ENCODING_LE_BFIELD` via `le_bytefield_table`. Macros `ENCODE_EVENT_START` and `ENCODE_EVENT_STOP` define event timestamp hooks but are not used in the shown implementation.

## Control Flow
Initialization installs `le_bytefield_table`, calls its `init_fun`, writes an 8-byte generic header containing `PVFS2_PROTO_VERSION` and encoding type in BMI byte order, and records the table entry's `enc_type`. Encode records destination and encoding type on `PINT_encoded_msg`, then dispatches request or response encode by message type. Decode validates that the message is at least the generic header size, extracts protocol version and encoding type, rejects unsupported encoding, rejects incompatible major versions, rejects too-new request minor versions and too-old response minor versions, then dispatches to the matching table entry with the payload pointer after the header. Release functions dispatch to concrete release hooks if the encoding type is valid.

## State and Persistence
The encoding table is process-global initialization state. Encoded/decoded buffers are owned by concrete modules and released via dispatcher release APIs. No durable persistence exists.

## Dependencies and Integration Points
Depends on BMI address types, byte swapping, request protocol constants, event/id utilities, `PINT_encoding_table_values`, and the little-endian bytefield module. It is the API used by clients, servers, and BMI send/receive paths that need serialized `PVFS_server_req` and `PVFS_server_resp` messages.

## Risks
Only one concrete encoding is installed; unsupported types fail. `PINT_encode` assumes initialization has populated the table. Header parsing uses unaligned integer casts that may be unsafe on strict-alignment platforms. Minor-version compatibility is directional: requests can be older but not newer than server; responses can be newer but not older than client. Release on invalid decodes quietly returns only for `enc_type == -1`.

## Test Signals
Initialize/finalize repeatedly under leak checking, encode/decode both request and response messages, reject short messages, reject bad encoding type, reject incompatible major/minor protocol versions, call release after failed decode, and verify max-size dispatch for every operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.c -->
