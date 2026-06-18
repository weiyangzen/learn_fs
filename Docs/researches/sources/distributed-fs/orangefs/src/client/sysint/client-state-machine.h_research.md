# sources/distributed-fs/orangefs/src/client/sysint/client-state-machine.h
## sources/distributed-fs/orangefs/src/client/sysint/client-state-machine.h

**Purpose:** Defines the client state-machine ABI: operation IDs, state structs for all sysint/mgmt operations, common helper macros, nested SM declarations, and post/test/release APIs.

**APIs and control flow:** The header declares initialization, post/test/testany/testsome, wait/release, I/O cancel, op-name lookup, and state-machine lookup/termination. It defines operation-specific structs for create, mkdir, symlink, lookup, rename, I/O, readdir/readdirplus, mgmt server lists, config fetch, xattrs, timers, security certs, and more. `PINT_client_sm` contains shared fields plus a union of operation states. Macros initialize getattr state, size arrays, credentials, and message-array params with per-filesystem server config or defaults.

**State and dependencies:** It binds sysint to PVFS types, job IDs, BMI addresses, flow descriptors, distribution/layout state, credentials/capabilities, cached config, hints, events, and generated SM externs.

**Risks and tests:** Struct layout is shared across generated `.sm` outputs, so changes have broad ABI impact. Macros assume variable names such as `sm_p` and can free/return from caller scopes. Operation enum/table order must remain synchronized with `client-state-machine.c`. Tests should include compilation of all generated SMs, enum-to-table mapping checks, credential null paths, config defaulting, and size-array allocation failure handling.
