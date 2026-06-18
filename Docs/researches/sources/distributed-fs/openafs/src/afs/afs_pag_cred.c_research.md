# sources/distributed-fs/openafs/src/afs/afs_pag_cred.c

## Purpose
`afs_pag_cred.c` manages local PAG token and sysname state for the PAG callback/translator runtime. It stores a local mapping of cell names to synthetic cell numbers, sets/unsets tokens from pioctl payloads, serves credentials and sysnames to the NFS translator over PAGCB RPCs, and updates global sysname state.

## Important APIs, types, and functions
The file defines `struct afspag_cell`, `afs_xpagcell`, `afs_xpagsys`, `lastcell`, `cells`, and `primary_cell`. Cell helpers are `afspag_GetCell`, `afspag_GetPrimaryCell`, and `afspag_SetPrimaryCell`. Token pioctl handlers are `afspag_PUnlog` and `afspag_PSetTokens`. PAGCB service handlers are `SPAGCB_GetCreds` and `SPAGCB_GetSysName`. Sysname pioctl handling is in `afspag_PSetSysName`.

## Control flow
`afspag_GetCell` locks the cell list, returns an existing named cell, or allocates a new `afspag_cell`, duplicates the cell name, assigns the next synthetic cell number, links it into the list, and initializes the primary cell if absent. `afspag_PUnlog` finds all `unixuser` entries for the current PAG or uid and clears token state, vice id, and token storage.

`afspag_PSetTokens` parses a pioctl payload containing ticket length, ticket bytes, clear token length, clear token, optional primary flag, and optional cell name. It can request setting the parent PAG, resolves the target cell, identifies the current PAG or uid, obtains a write-locked `unixuser`, replaces tokens with a new rxkad token, updates auth stats, marks token state valid, sets primary state, and records token time.

`SPAGCB_GetCreds` accepts calls only from the configured NFS server host and port, counts matching `unixuser` records, allocates a `CredInfos` array, copies valid rxkad token material and cell names into RPC-owned allocations, and handles cleanup on allocation failure. `afspag_PSetSysName` validates superuser-supplied sysnames, rejects dangerous `.` and `..`, updates `afs_global_sysnames`, bumps `afs_sysnamegen`, and marks the forwarded command so the server applies it to all PAGs. `SPAGCB_GetSysName` copies current sysnames into a PAGCB response.

## State and persistence behavior
State is in memory: synthetic cell list, primary cell pointer, global sysname list/generation, and token state in `unixuser` records. Tokens are sensitive runtime credentials and are freed or copied into RPC responses as needed.

## Dependencies and integration points
Dependencies include `unixuser` hash tables and token APIs, rxkad token structures, PAG extraction, pioctl payload layouts, PAGCB XDR types, Rx peer/host checks, sysname locks, OSI allocation/string duplication, and the translator init state from `afs_pag_call.c`.

## Risks and edge cases
Security depends on `SPAGCB_GetCreds` restricting callers to `afs_nfs_server_addr:7001`, superuser checks for sysname mutation, and correct PAG/uid selection when no PAG exists. Payload parsing in `afspag_PSetTokens` must match pioctl marshalling exactly. Allocation failures in RPC response construction require careful partial cleanup. The `set_parent_pag` path warns and mutates process PAGs, which is sensitive.

## Test signals
Test token set/unlog for uid and PAG users, default primary cell behavior, explicit cell creation, primary token flag handling, parent-PAG request warning, PAGCB credential export only from the configured host, multi-cell credential responses, sysname validation and propagation, and allocation-failure cleanup paths.
