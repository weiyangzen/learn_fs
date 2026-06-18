# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsnewcreds.c

## Purpose
Implements the AFS page in the NetIDMgr new-credentials and per-identity configuration UI, plus the credential-acquisition message path that obtains or renews AFS tokens after Kerberos succeeds. It owns the editable list of AFS cells, optional realms, token methods, conflict markers, and per-identity persistence.

## Important APIs, Types, And Functions
The file works around `afs_cred_list`/`afs_cred_row` from `afsnewcreds.h`. Row helpers allocate, flush, delete, and populate rows from KCDB AFS credentials. `afs_cred_get_identity_creds()` merges per-identity configuration, global defaults, root-cell/default-cell discovery, realm registry keys, and live KCDB credentials. `afs_dlg_proc()` is the dialog procedure for the new-credentials panel and identity configuration panel. `afs_msg_newcred()` handles NetIDMgr credential-acquisition submessages and ultimately calls `afs_klog()` for each selected row.

## Control Flow
Initialization creates list columns, image lists, method combo entries, and tooltips. Dialog setup fills LRU cells/realms, selects the root cell, loads rows for the active identity, and updates credential text. Add/delete commands validate cell and realm characters, detect cell ownership conflicts across configured identities, and update the row list. During `KMSG_CRED_PROCESS`, the code refuses to run if Kerberos 5 failed, builds a row list from either dialog state or renewal context, applies global method overrides, obtains tokens cell-by-cell, optionally follows linked cells, refreshes token inventory, annotates new KCDB credentials with identity/realm/method, and persists identity data.

## State And Persistence
Persistent state is stored under NetIDMgr config spaces: per-identity `AfsCred/AFSEnabled`, `AfsCred/Cells`, per-cell `MethodName` and `Realm`, global `LRUCells`, `LRURealms`, `DefaultCells`, and global cell-to-identity mappings. It also reads `HKLM\SOFTWARE\OpenAFS\Client\Realms\<realm>` for realm-scoped defaults. Runtime state includes dialog `dirty`, tooltip visibility, critical section protection, row flags, and `nct->credtext`.

## Dependencies And Integration Points
Depends heavily on NetIDMgr KCDB, configuration, credential wizard, alert, action-context, and message APIs; Win32 common controls/tooltips; resource IDs from `langres.h`; AFS helpers in other plugin files (`afs_klog`, `afs_list_tokens_internal`, `afs_method_describe`, method lookup, root-cell lookup, HTML help); and Kerberos credential types. It is called from `afsplugin.c` when credential-acquisition messages arrive.

## Risks
Memory ownership is manual and row deletion compacts arrays after freeing only the removed slot, so stale pointers would be serious if external code cached row addresses. Configuration reads and registry fallbacks have multiple early exits that can leave partial defaults. Conflict resolution can remove the same cell from other identities. The process path uses UI dialog state while holding `d->cs`; blocking token acquisition under that lock can affect UI responsiveness. Linked-cell handling uses a `goto` loop that relies on `afs_klog()` clearing or setting `linkedCell` correctly.

## Test Signals
Useful tests are UI add/delete validation, identity switching, conflict prompts, persistence round trips for `MethodName`/`Realm`, renewal context filtering, linked-cell token acquisition, Kerberos failure handling, and registry/default-cell fallback. No direct unit tests were present in this subset.
