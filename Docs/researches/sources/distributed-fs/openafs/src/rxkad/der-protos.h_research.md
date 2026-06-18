## sources/distributed-fs/openafs/src/rxkad/der-protos.h

### Purpose
`der-protos.h` is a generated Heimdal DER/ASN.1 prototype header vendored under rxkad for Kerberos v5 ticket support.

### Important APIs, Types, And Functions
It declares fuzzer hooks, copy/free/decode/encode routines for Heimdal ASN.1 types, DER primitive getters and putters, length calculators, tag/class/type name mapping, OID and integer parsing/printing, comparison helpers, and `heim_any` helpers.

### Control Flow
The header has no executable flow. The declared APIs follow DER conventions: decode/get functions consume buffers and return consumed sizes, put/encode functions write backwards into bounded buffers, free functions release nested allocations, and length functions compute encoded sizes.

### State, Persistence, And Dependencies
It has no state, uses an include guard, supports C++ linkage, and is hidden under `#ifndef DOXY`. It depends on Heimdal ASN.1 typedefs from surrounding headers such as `der.h` and generated v5 headers.

### Integration Points
rxkad Kerberos v5 ticket code includes this through `der.h` to encode/decode tickets and authorization data. Fuzzer hooks allow generated ASN.1 fuzz infrastructure to drive decoders.

### Risks
As generated API surface, manual drift from implementation sources causes compile/link mismatches. Many routines allocate memory through Heimdal conventions, so callers must match decode/copy calls with the correct free functions.

### Test Signals
Compile/link coverage against DER implementation, ASN.1 encode/decode round trips, malformed length/tag tests, memory-leak checks for every decode/free pair, and fuzzer builds are key signals.
