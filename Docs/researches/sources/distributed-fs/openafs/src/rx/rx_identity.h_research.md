# Research: sources/distributed-fs/openafs/src/rx/rx_identity.h

## sources/distributed-fs/openafs/src/rx/rx_identity.h

### Purpose
`rx_identity.h` defines the RX identity structure and identity management API.

### Important APIs and Types
- `rx_identity_kind` values: `RX_ID_SUPERUSER`, `RX_ID_KRB4`, and `RX_ID_GSS`.
- `struct rx_identity` with `kind`, optional `displayName`, and `struct rx_opaque exportedName`.
- Prototypes for creation, population, matching, copying, content-freeing, and full freeing.

### Control Flow and State
The header only declares structure and operations. Implementations allocate owned copies of display and exported names.

### Dependencies and Integration Points
Includes `rx/rx_opaque.h`. It is meant for RX security layers and callers that need a common identity payload independent of the specific security mechanism.

### Risks and Edge Cases
Because ownership is in the implementation, users must know whether a function replaces existing contents without freeing. Kind values include a negative superuser sentinel, so serialization or casts to unsigned types need care.

### Test Signals
Compile tests for consumers, identity serialization tests in security layers, and memory ownership tests around copy/free are appropriate.
