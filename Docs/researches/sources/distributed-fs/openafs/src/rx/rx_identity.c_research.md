# Research: sources/distributed-fs/openafs/src/rx/rx_identity.c

## sources/distributed-fs/openafs/src/rx/rx_identity.c

### Purpose
`rx_identity.c` implements allocation, copying, comparison, population, and freeing of RX identity objects, which pair an identity kind, display name, and opaque exported name.

### Important Functions
- `rx_identity_match` compares kind, exported-name length, and exported-name bytes.
- `rx_identity_populate` zeroes a structure, sets kind, copies display name, and populates the exported opaque name.
- `rx_identity_new` allocates and populates a new identity.
- `rx_identity_copy` and `rx_identity_copyContents` duplicate identity contents.
- `rx_identity_freeContents` frees display name and opaque data.
- `rx_identity_free` clears caller pointer, frees contents, and frees the identity.

### Control Flow and State
Population and copy functions replace existing contents without freeing them first, as documented. Free functions clear owned pointers after release. State is heap memory allocated through `rxi_Alloc`/`rxi_Free`; no durable persistence.

### Dependencies and Integration Points
Depends on `rx/rx.h`, `rx/rx_identity.h`, and `rx_opaque` helpers. Used by security/authentication layers that need to carry a typed RX identity.

### Risks and Edge Cases
- `rx_identity_populate` can leak existing contents if called on a populated identity without first freeing.
- Allocation failures from display-name allocation and `rx_opaque_populate` are not reported; partial objects are possible.
- `rx_identity_match` assumes non-NULL identity pointers and valid exportedName buffers when length is non-zero.
- `rx_identity_freeContents` frees displayName with `strlen(displayName)`, not including the NUL byte allocated by populate.

### Test Signals
Tests should cover match/non-match by kind/name bytes, NULL display name, zero-length exported name, copy independence, repeated populate leak checks, allocation-failure behavior, and free pointer clearing.
