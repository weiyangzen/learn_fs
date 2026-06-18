# sources/distributed-fs/ceph-client/drivers/firmware/google/vpd_decode.h

Purpose: Defines the public interface and constants for Google VPD decoding.

Important APIs/types/functions: Enumerates `VPD_OK`/`VPD_FAIL` and VPD record types including terminator, string, info, and implicit terminator. Defines `vpd_decode_callback` and declares `vpd_decode_string()`.

Control flow: No executable flow. Consumers pass a buffer, consumed offset, callback, and callback argument to the decoder.

State and persistence behavior: No state. The callback contract passes borrowed pointers into caller-owned VPD storage.

Dependencies and integration points: Depends on Linux integer types. Included by `vpd.c` and implemented by `vpd_decode.c`.

Risks and test signals: Callback callers must not assume null-terminated key/value strings. ABI is internal to the module composite. Test signals are compiler type checking and parser unit-style tests with binary VPD blobs.
