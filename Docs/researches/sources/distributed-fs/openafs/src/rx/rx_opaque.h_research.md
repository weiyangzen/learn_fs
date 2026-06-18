# Research: sources/distributed-fs/openafs/src/rx/rx_opaque.h

## sources/distributed-fs/openafs/src/rx/rx_opaque.h

### Purpose
`rx_opaque.h` defines the RX opaque byte-buffer type and the API for allocation, copying, secure freeing, comparison, and debug stringification.

### Important APIs and Types
- `struct rx_opaque { size_t len; void *val; }`.
- `struct rx_opaque_stringbuf { char sbuf[100]; }`.
- `RX_EMPTY_OPAQUE` initializer.
- Prototypes for `rx_opaque_new`, `rx_opaque_alloc`, `rx_opaque_populate`, `rx_opaque_copy`, content and object free/zero-free helpers, `rx_opaque_cmp`, and `rx_opaque_stringify`.

### Control Flow and State
The header has no executable flow. It defines ownership-bearing structures whose storage is managed by `rx_opaque.c`.

### Dependencies and Integration Points
Included by `rx_identity.h` and security-related consumers. It intentionally keeps the representation simple for copying and wire/exported-name uses.

### Risks and Edge Cases
Because `val` is a raw pointer and `len` is public, consumers can create invalid states such as non-zero length with NULL value. The 100-byte stringify buffer is for diagnostics only and cannot uniquely identify large opaque values.

### Test Signals
Consumer tests should validate initialization with `RX_EMPTY_OPAQUE`, ownership transfer assumptions, and comparison/stringification behavior.
