# sources/distributed-fs/openafs/src/kauth/knfs.c

## Purpose
Implements `knfs`, a utility for copying, displaying, or removing AFS tokens for an NFS translator client identified by host and UID, and optionally setting that client's `@sys` value.

## Important APIs, Types, And Functions
Important helpers are `SetSysname`, `GetTokens`, `NFSUnlog`, `NFSCopyToken`, `cmdproc`, and `main`. It defines a local `ClearToken` layout matching cache-manager expectations and builds raw `ViceIoctl` buffers with NFS exporter pioctl headers.

## Control Flow
`main` registers `-host`, `-id`, `-sysname`, `-unlog`, and `-tokens`. `cmdproc` resolves the host, parses or derives UID, then either displays remote tokens, unlogs the remote identity, or copies local AFS service tokens into the NFS translator and optionally sets sysname. Token copy enumerates local `afs` service tokens, retrieves each token, constructs encrypted-ticket and clear-token payloads plus cell name, and sends `_VICEIOCTL(99)` pioctls. Token display sends get-token pioctls and formats expiration and identity information.

## State And Persistence
State changes occur in the cache manager/NFS translator token table and sysname state through pioctl calls. The process itself keeps only stack buffers.

## Dependencies And Integration Points
It depends on ktc token APIs, pioctl, Vice ioctl conventions, host utilities, command parsing, and hard-coded pioctl sub-opcode numbers for set token, get token, unlog, and sysname.

## Risks And Test Signals
Risks include raw fixed-size buffer assembly, hard-coded pioctl indexes, bounds sensitivity around ticket and cell-name copy, legacy clear-token layout, host/UID authorization failures, and IPv4-only address handling. Test signals include copy/display/unlog flows, multiple cell tokens, expired-token display, UID wildcard/default behavior, sysname set, translator passwd-sync error messages, oversized ticket rejection, and pioctl error mapping.
