## sources/distributed-fs/openafs/src/rxgen/rxgen_consts.h

### Purpose
`rxgen_consts.h` centralizes rxgen generated-code return constants and compile-time bounds for packages and procedure names.

### Important APIs, Types, And Functions
It defines `RXGEN_SUCCESS`, client/server marshal and unmarshal errors, decode/opcode errors, XDR-free errors, call wait constants, `MAX_PACKAGES`, `MAX_FUNCTION_NAME_LEN`, `MAX_FUNCTIONS_PER_PACKAGE`, and `MAX_FUNCTIONS_PER_INTERFACE`.

### Control Flow
There is no runtime flow. Generated client/server stubs return these negative error codes when XDR operations fail or an unknown opcode is received.

### State, Persistence, And Dependencies
The header is guarded by `_RXGEN_CONSTS_` and has no mutable state. Its constants shape static arrays in `rpc_parse.c`.

### Integration Points
Included by `rpc_util.h`, generated stubs, and rxgk placeholder procedures. Runtime Rx code observes these values as procedure return errors.

### Risks
The numeric error values are arbitrary and must remain stable for generated-code compatibility. Increasing package/function limits changes static memory footprint and may reveal other fixed buffers.

### Test Signals
Generated stub tests should assert expected return codes for marshal/unmarshal/opcode failures and boundary tests should exercise package and function count limits.
