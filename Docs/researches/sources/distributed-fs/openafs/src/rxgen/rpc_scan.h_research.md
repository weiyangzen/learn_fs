## sources/distributed-fs/openafs/src/rxgen/rpc_scan.h

### Purpose
`rpc_scan.h` declares the rxgen token kinds and the token carrier structure shared by the scanner, parser, and utility diagnostics.

### Important APIs, Types, And Functions
`enum tok_kind` covers identifiers, string constants, punctuation, standard RPCL keywords, rxgen extensions, direction markers, `afsUUID`, and EOF. `struct token` pairs a `tok_kind` with the token text pointer.

### Control Flow
There is no runtime flow; ordering must remain compatible with scanner symbol tables and diagnostic string tables in `rpc_scan.c` and `rpc_util.c`.

### State, Persistence, And Dependencies
Token text may point at static reserved-word strings or scanner-allocated memory. The header has no guard macro in this copy, so repeated inclusion relies on existing source include patterns.

### Integration Points
`rpc_parse.c` switches on these token kinds to build definitions, while `rpc_util.c` maps them back to display strings for `expected*` errors.

### Risks
Adding or reordering tokens requires synchronized updates to scanner recognition and diagnostic tables. Lack of an include guard can become a build issue if included indirectly more than once in a translation unit.

### Test Signals
Build tests plus scanner fixtures for all token kinds provide coverage. Any new token should have parser, scanner, and diagnostic coverage together.
