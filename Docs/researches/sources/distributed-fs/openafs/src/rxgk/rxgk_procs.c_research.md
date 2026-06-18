## sources/distributed-fs/openafs/src/rxgk/rxgk_procs.c

### Purpose
`rxgk_procs.c` contains server-side RPC procedure implementations for optional rxgk GSS/token-combination services.

### Important APIs, Types, And Functions
When `AFS_RXGK_GSS_ENV` is defined, it defines `SRXGK_GSSNegotiate`, `SRXGK_CombineTokens`, and `SRXGK_AFSCombineTokens`.

### Control Flow
All three procedures currently return `RXGEN_OPCODE`, indicating unimplemented or unsupported operations to callers. No input is decoded here beyond rxgen-generated wrapper behavior.

### State, Persistence, And Dependencies
There is no persistent state in this file. It includes Rx, identity, public rxgk, and private rxgk headers only under the GSS build flag.

### Integration Points
Generated server stubs from `rxgk_int.xg` would call these `SRXGK_*` functions. The makefile has a placeholder for future GSSAPI linkage, consistent with these stubs being inactive/incomplete.

### Risks
If `AFS_RXGK_GSS_ENV` is enabled and clients expect negotiation or token combination, they receive opcode errors. The file is a compatibility placeholder rather than a complete service implementation.

### Test Signals
Build with and without `AFS_RXGK_GSS_ENV`. Under the flag, RPC tests should assert these operations fail with `RXGEN_OPCODE` until real implementations are added.
