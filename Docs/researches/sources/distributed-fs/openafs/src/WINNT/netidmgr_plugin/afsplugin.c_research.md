# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsplugin.c

## Purpose
Core NetIDMgr plugin message dispatcher and registration file. It registers AFS as a credential type, installs custom KCDB data types/attributes, hooks configuration panels and help action, manages extension message type registration, refreshes/destroys tokens, and delegates credential-acquisition work.

## Important APIs, Types, And Functions
Global IDs include AFS/Kerberos credential types, AFS extension message type, custom principal/method KCDB types, transient AFS attributes, the shared AFS credset, subscription, and help action. `afs_plugin_cb()` dispatches messages. Principal type callbacks stringify/validate/compare/duplicate `ktc_principal`. `afs_type_method_toString()` localizes method descriptions. `afs_msg_system()`, `afs_msg_cred()`, and `afs_msg_act()` handle lifecycle, token refresh/destroy, new-credentials routing, and help action launching.

## Control Flow
On `KMSG_SYSTEM_INIT`, it optionally imports newer NetIDMgr APIs, sets an initial service-stopped icon, registers the AFS credential type and KCDB types/attributes, creates `afs_credset`, discovers Kerberos credential type IDs, registers config nodes, registers/subscribes the AFS extension message type, removes an `afscreds.exe` shortcut if configured, adds AFS Help under the Help menu, lists existing tokens, and sets `KERBEROSLOGIN_NEVER_PROMPT=1`. On exit, it removes icons/actions, unregisters message types, credential types, attributes, data types, and deletes the credset.

## State And Persistence
Runtime globals carry registered IDs and handles. It reads plugin configuration for `Disableafscreds` and relies on config schemas opened by `main.c`. It does not itself persist token data.

## Dependencies And Integration Points
Integrates with NetIDMgr KMM/KMQ/KCDB/KHUI/KHERR APIs, resources, config dialog procedures, icon/help helpers, extension dispatch in `afsext.c`, token functions in `afsfuncs.c`, and new-credential logic in `afsnewcreds.c`.

## Risks
Initialization has many registrations with partial-failure exits; rollback is mostly deferred to module unload. API-version compatibility uses dynamic function pointers when compiled against older SDKs. Help menu modification must balance lock/unlock and refresh. Destroying selected AFS credentials calls `afs_unlog_cred()` for each matching cred, so context filtering correctness matters.

## Test Signals
Plugin load/unload under old and new NetIDMgr API versions, token refresh, destroy selected tokens, help action insertion/removal, extension message registration, and new/renew credential dispatch are the main signals.
