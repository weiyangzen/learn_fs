# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/afspext.c

## Purpose
Sample extension implementation stubs for AFS extension messages.

## Important APIs, Types, And Functions
`handle_AFS_MSG_RESOLVE_TOKEN()` receives `afs_msg_resolve_token` and should set `ident` and `method` if it can identify a token. `handle_AFS_MSG_KLOG()` receives `afs_msg_klog` and should obtain a token. `handle_AFS_MSG()` dispatches extension message subtypes.

## Control Flow
The dispatcher switches on `AFS_MSG_RESOLVE_TOKEN` and `AFS_MSG_KLOG`, returning `KHM_ERROR_NOT_IMPLEMENTED` for both stock stubs and for unknown messages.

## State And Persistence
No persistent state is implemented. A real extension would likely use NetIDMgr identity handles and any external authentication state required by its token method.

## Dependencies And Integration Points
Includes sample `credprov.h` and core `afspext.h`. It is reached through the subscription created during sample plugin initialization in `plugin.c`.

## Risks
As shipped, enabling `provide_token_acq` in the sample registers a method that cannot actually acquire or resolve tokens. Implementers must respect ownership rules for identity handles returned in resolve-token messages.

## Test Signals
After implementing, test resolve-token success/failure, klog success/failure, and Auto-method fallback behavior when this extension is tried after stock methods.
