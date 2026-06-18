# sources/distributed-fs/ceph-client/drivers/firmware/google/vpd_decode.c

Purpose: Decodes Google VPD length-prefixed records and invokes a callback for string key/value entries.

Important APIs/types/functions: `vpd_decode_len()` decodes a variable-length 7-bit quantity with continuation bit. `vpd_decode_entry()` consumes one length-prefixed entry and validates bounds. `vpd_decode_string()` parses record type, key, and value, then calls a user-provided callback for `VPD_TYPE_STRING`.

Control flow: Decoding starts at `*consumed`. For INFO or STRING records it increments past the type, decodes key and value entries, updates `*consumed`, and only emits callback output for STRING records. Unknown types, out-of-range lengths, and exhausted buffers return `VPD_FAIL`.

State and persistence behavior: Stateless except for updating the caller's `consumed` offset. It does not allocate or copy data; callback receives pointers into the original input buffer.

Dependencies and integration points: Used by `vpd.c` to create sysfs attributes from VPD blobs. Depends on constants and callback typedef from `vpd_decode.h`.

Risks and test signals: Integer underflow is mitigated by repeated `max_len - consumed` checks, but callers must pass valid `consumed` pointers and immutable buffers. Test length encodings at boundaries, truncated entries, INFO records, terminator/implicit terminator behavior, and callback error propagation.
