# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsnewcreds.h

## Purpose
Declares the dialog and row model used by the AFS new-credentials UI and identity configuration panel.

## Important APIs, Types, And Functions
`afs_cred_row` stores a wide-character cell, optional realm, token method, and row flags. `afs_cred_list` owns the dynamic row array. `afs_dlg_data` binds a credential wizard object, row list, enable/dirty flags, tooltip handle, list-view image indexes, synchronization, and configuration-dialog identity state. Public functions include row lifecycle helpers, context/identity credential loaders, row refresh, persistence, dialog procedure, and `afs_msg_newcred()`.

## Control Flow
This header defines constants that drive `afsnewcreds.c`: list subitem indexes, allocation granularity, tooltip timer ID, and flags representing validation, existence, deletion, token acquisition, ownership conflicts, expiration, and config origin.

## State And Persistence
The header itself stores no state, but its structures model persistent per-identity AFS cell choices and transient UI/token state. `DLGROW_FLAG_DONE` bridges the acquisition loop and persistence because only completed rows are recorded in the global cell map.

## Dependencies And Integration Points
Requires NetIDMgr handles and UI types, Win32 dialog types, `afs_tk_method` from `afspext.h`, and resource/control conventions from the plugin.

## Risks
Flags are bitmasks with overlapping lifecycle meanings; consumers must preserve bits carefully. `afs_dlg_data` is shared between UI messages and credential processing and must remain protected by its critical section.

## Test Signals
Compile-time coverage should verify all declarations match `afsnewcreds.c`. Runtime tests should exercise flag combinations in list rendering and acquisition.
