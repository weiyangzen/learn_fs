# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afspext.h

## Purpose
Defines the public extension API between the core AFS NetIDMgr plugin and separate extension plugins that can resolve tokens or provide additional token acquisition methods.

## Important APIs, Types, And Functions
Defines cell/host limits, stock token method IDs (`AFS_TOKEN_AUTO`, `AFS_TOKEN_KRB5`, `AFS_TOKEN_KRB524`, `AFS_TOKEN_KRB4`), plugin API version, message type name `AfsExtMessage`, message subtypes `AFS_MSG_ANNOUNCE`, `AFS_MSG_RESOLVE_TOKEN`, and `AFS_MSG_KLOG`, and payload structures `afs_msg_announce`, `afs_msg_resolve_token`, `afs_conf_cell`, and `afs_msg_klog`.

## Control Flow
Extension plugins first send `AFS_MSG_ANNOUNCE` by synchronous message with a subscription handle and optional token-acquisition description. The core plugin later sends resolve-token broadcasts/unicasts or klog requests to extensions that announced token-acquisition support.

## State And Persistence
The API itself has no persistence, but announcements create runtime extension registry state in the core plugin. `token_acq.method_id` is an output assigned by the core plugin and then used in future method selections.

## Dependencies And Integration Points
Uses NetIDMgr `khm_*` types, AFS `ktc_token` and `ktc_principal` structures, WinSock `sockaddr_in`, and the plugin message queue. The sample extension in this subset includes this header.

## Risks
Structures include raw pointers and require synchronous send for announcement because there is no cleanup callback. Version skew is handled only by `cbsize` and `version`; extensions must check and initialize all fields. ANSI cell/realm fields in klog messages require explicit conversion by Unicode-heavy callers.

## Test Signals
Exercise extension announcement, assigned method IDs, resolve-token fallback, klog dispatch to a method extension, and rejection of incompatible versions.
