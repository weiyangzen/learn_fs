<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/zbase32.c -->
# sources/cloud-native/ostree/src/libotutil/zbase32.c

## Purpose
Implements z-base-32 encoding for binary buffers using Zooko Wilcox-O'Hearn's alphabet.

## Important APIs and Types
The exported function is `zbase32_encode`. Internal `zstr` and `czstr` pair a length with mutable or const byte buffers. Helpers include `new_z`, `divceil`, `b2a_l_extra_Duffy`, `b2a_l`, and `b2a`.

## Control Flow
`zbase32_encode` wraps input data in `czstr`, calls `b2a`, and returns the allocated output buffer. The encoder allocates the maximum needed quintet string, walks input from the end using Duff's device over 5-byte groups, maps 5-bit values through the z-base-32 alphabet, then truncates unused trailing quintets for non-byte-aligned bit lengths.

## State and Persistence
No global mutable state exists. The returned string is heap allocated with `malloc` and must be freed by the caller with a compatible allocator.

## Dependencies and Integration Points
Uses libc allocation/string headers and `zbase32.h`. OSTree may use this for compact human-friendly encodings where z-base-32 compatibility matters.

## Risks
The implementation is old and pointer-arithmetic heavy; boundary conditions around zero-length input, allocation failure, and partial groups need coverage. It returns `malloc` memory rather than GLib `g_malloc`, so ownership conventions must be clear.

## Test Signals
Known-vector tests for z-base-32, empty and one-to-five byte inputs, large inputs, allocation-failure handling where injectable, and leak checks for caller ownership are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/zbase32.c -->
