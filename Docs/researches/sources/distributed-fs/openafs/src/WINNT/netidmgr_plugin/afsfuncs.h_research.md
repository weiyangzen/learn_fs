# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsfuncs.h

## Purpose

`afsfuncs.h` declares the AFS service, token listing, token acquisition, token deletion, error reporting, and cell/realm compatibility helpers implemented in `afsfuncs.c`.

## Important APIs, types, and functions

Declared functions are `afs_is_running`, `afs_princ_to_string`, `afs_list_tokens`, `afs_find_token`, `afs_list_tokens_internal`, `afs_klog`, `afs_unlog`, `afs_unlog_cred`, `GetServiceStatus`, `ServiceControl`, `afs_report_error`, and `afs_check_for_cell_realm_match`. The `afs_klog` signature takes identity, service, cell, realm, lifetime, token method, output expiration, and output linked-cell buffer.

## Control flow

The header has no runtime flow, but its API shape exposes the main lifecycle: check service, obtain/list tokens, find/delete tokens, and report/control service state.

## State and persistence behavior

Callers should expect these functions to interact with OpenAFS token state, NetIDMgr credential sets, and the Windows Service Control Manager. `afs_klog` can return token expiration and linked cell through caller-provided outputs.

## Dependencies and integration points

The header assumes `afscred.h` has already provided `khm_handle`, `afs_tk_method`, and OpenAFS principal/token types. It is included back into `afscred.h` and used by dialogs and new-credential code.

## Risks and edge cases

Because it declares `GetServiceStatus` and `ServiceControl` with generic names, there is collision risk with other utility layers. Buffer-size expectations for `afs_princ_to_string` and `linkedCell` are implicit in the implementation rather than encoded in the prototype.

## Test signals

Compile tests should ensure the header is included through `afscred.h`. Runtime tests are the `afsfuncs.c` service/token scenarios, with special attention to output buffer sizing.
