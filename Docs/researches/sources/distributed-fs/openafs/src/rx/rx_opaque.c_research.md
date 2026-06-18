# Research: sources/distributed-fs/openafs/src/rx/rx_opaque.c

## sources/distributed-fs/openafs/src/rx/rx_opaque.c

### Purpose
`rx_opaque.c` implements owned variable-length byte buffers used by RX identity and security-related code.

### Important Functions
- Allocation/population: `rx_opaque_new`, `rx_opaque_alloc`, `rx_opaque_populate`, and `rx_opaque_copy`.
- Cleanup: `rx_opaque_freeContents`, `rx_opaque_zeroFreeContents`, `rx_opaque_free`, and `rx_opaque_zeroFree`.
- Comparison/debug: `rx_opaque_cmp` and `rx_opaque_stringify`.

### Control Flow and State
`rx_opaque_new` allocates the struct and populates it. `rx_opaque_alloc` allocates a zero-filled buffer and stores length. `rx_opaque_populate` resets the destination to empty, allocates new storage if data and length are non-zero, and copies bytes. Cleanup functions free contents and clear fields; zero-free variants wipe data before freeing. `rx_opaque_cmp` compares common-prefix bytes and then length. `rx_opaque_stringify` writes `<len>:<hex>` into a fixed 100-byte stack-owned output buffer supplied by caller.

### Dependencies and Integration Points
Depends on `rxi_Alloc`, `rxi_Free`, `opr_min`, `osi_Assert`, and `rx_opaque.h`. Used by `rx_identity.c` and likely security mechanisms needing exported binary names or tokens.

### Risks and Edge Cases
- Populate/copy functions replace existing contents without freeing them, so callers must avoid leaks.
- `rx_opaque_new` does not handle populate failure by freeing the allocated struct.
- `rx_opaque_alloc` with length zero depends on allocator behavior; populate avoids that path for zero length.
- `rx_opaque_cmp` asserts if length is non-zero and value is NULL.
- `rx_opaque_stringify` truncates large buffers silently except for the length prefix.

### Test Signals
Unit tests should cover zero-length and NULL buffers, copy independence, comparison ordering by bytes and length, zero-free wiping, stringify truncation, and allocation-failure cleanup behavior.
