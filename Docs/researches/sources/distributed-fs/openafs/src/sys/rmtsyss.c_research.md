# sources/distributed-fs/openafs/src/sys/rmtsyss.c

## Purpose
`rmtsyss.c` implements the server-side RMTSYS RPC handlers used by `rmtsysd` or afsd-started RMTSYS service to perform local `setpag` and `pioctl` on behalf of remote clients.

## Important APIs, types, and functions
Exports include `rmtsysd`, `SRMTSYS_SetPag`, `SRMTSYS_Pioctl`, and `rmt_Quit`. Important macros are `SETCLIENTCONTEXT`, `PIOCTL_HEADER`, `PSETPAG`, `PSetClientContext`, and `NFS_EXPORTER`.

## Control flow
`rmtsysd` starts the RX service with null security. `SRMTSYS_SetPag` builds a context blob from RX peer host and supplied uid/groups, calls local `lpioctl` with `_VICEIOCTL(PSetClientContext)`, and interprets `errno == PSETPAG` as a returned PAG. `SRMTSYS_Pioctl` prepends the same context blob to converted input data, maps `NIL_PATHP` to a null local path, calls local `lpioctl`, converts output to network order on success, and returns pioctl errno through an out parameter while keeping the RPC return value zero.

## State and persistence behavior
Handlers do not persist their own state, but they forward requests that mutate local AFS cache-manager state and PAG/token context. Allocated pioctl input buffers are freed per request.

## Dependencies and integration points
It depends on RX call peer inspection, generated RMTSYS server stubs, local `lpioctl`, pioctl conversion routines, and kernel support for `PSetClientContext`.

## Risks
The service uses null security and trusts client-provided credential fields. Input length plus header allocation must fit memory and local pioctl expectations. Returning zero for pioctl failures is protocol-dependent and easy for callers to mishandle.

## Test signals
Test remote setpag success/failure, returned PAG extraction, NIL and non-NIL paths, pioctl errno propagation, conversion of token/ACL/status pioctls, allocation failure, and concurrent RX requests.
