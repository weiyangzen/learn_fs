## sources/distributed-fs/openafs/src/rxgk/rxgk_types.h

### Purpose
`rxgk_types.h` exposes the minimal public rxgk type surface needed before including the full rxgk API.

### Important APIs, Types, And Functions
It defines `rxgk_key` as an opaque pointer to `struct rxgk_key_s`.

### Control Flow
There is no executable flow. The opaque typedef allows public APIs to pass keys without exposing the RFC3961 backend representation.

### State, Persistence, And Dependencies
The concrete state is defined in `rxgk_crypto_rfc3961.c`. Callers can only hold and pass the pointer and must release it through `rxgk_release_key()`.

### Integration Points
Included by `rxgk.h` and installed as a public header. It decouples token/security-object APIs from crypto backend internals.

### Risks
Because `rxgk_key` is a pointer type, NULL is possible and misuse is not type-prevented. ABI depends on keeping the struct incomplete to external callers.

### Test Signals
Public-header compile tests should ensure users can declare `rxgk_key` and call API functions without including private crypto headers.
