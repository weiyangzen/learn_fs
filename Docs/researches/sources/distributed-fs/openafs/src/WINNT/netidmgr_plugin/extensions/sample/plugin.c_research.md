# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/plugin.c

## Purpose
Sample plugin message processor that announces an AFS extension and optionally registers a new token acquisition method.

## Important APIs, Types, And Functions
Globals `msg_type_afs`, `g_credset`, and assigned `tk_method` track extension integration. `handle_kmsg_system()` handles plugin lifecycle. `plugin_msg_proc()` dispatches NetIDMgr system messages and AFS extension messages.

## Control Flow
On `KMSG_SYSTEM_INIT`, the plugin finds the AFS extension message type, creates a unicast subscription for `handle_AFS_MSG`, fills an `afs_msg_announce` structure, loads token method descriptions, synchronously sends `AFS_MSG_ANNOUNCE`, and saves the returned method ID. Optional configuration-panel registration is guarded by `USE_CONFIGURATION_PANELS`. On exit, it removes the optional config node. AFS messages are forwarded to `handle_AFS_MSG()`.

## State And Persistence
Runtime state includes message type ID and token method ID assigned by the core plugin. Optional config registration adds UI state but no sample persistence.

## Dependencies And Integration Points
Integrates with core AFS plugin through `AFS_MSG_TYPENAME`, sample handlers in `afspext.c`, NetIDMgr KMQ/KHUI, and resource strings from `langres.h`.

## Risks
Announcement uses stack-backed string buffers and must remain synchronous, matching the API contract. Since sample handlers return not implemented, registering `provide_token_acq=TRUE` creates a visible method that fails until filled in.

## Test Signals
Core plugin present/absent startup, subscription cleanup on failed announce, assigned method ID availability, optional config registration, and dispatch of AFS messages.
