# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_security.cpp

Purpose: implements the AFS Server Manager server-security property sheet, covering server administrator lists and BOS encryption keys. It also implements create-key input parsing, random-key retrieval, and key display formatting.

Important APIs/functions: `Server_Key_SetDefaultView` initializes `gr.viewKey`. `Server_Security` opens or focuses a modeless two-tab property sheet. `Server_Lists_*` functions load, display, add, remove, and save the admin list. `Server_Keys_*` functions load, display, create, and delete server keys. `FormatServerKey` encodes an `ENCRYPTIONKEY` as backslash-prefixed octal triplets, and `ScanServerKey` reverses that format. `CreateKey_*` manages the modal key creation dialog.

Control flow: `Server_Security` allocates one `SVR_SECURITY_PARAMS` shared by both tabs and ref-counted across sheet lifetime. The list tab starts `taskSVR_ADMLIST_OPEN`; the key tab starts `taskSVR_KEYLIST_OPEN`. User edits mutate loaded `AfsClass` list structures in memory and dispatch save/create/delete tasks. Key create chooses the next version by scanning in-use keys and either sends a string password or raw parsed key data.

State and persistence: the shared params retain `LPADMINLIST` and `LPKEYLIST` until both tabs are destroyed. Key list column layout is persisted through `gr.viewKey` on destroy. Admin-list save increments `cRef` before dispatch so task-side notification/free behavior remains safe.

Dependencies/integration: uses property sheets, `PropCache`, `display.h`, `AfsAppLib_ShowBrowseDialog`, `AfsClass_AdminList_*`, `AfsClass_KeyList_*`, `AfsClass_AddKey/DeleteKey/GetRandomKey`, and the task queue.

Risks: `Server_Keys_OnEndTask_ListOpen` calls `Server_Lists_OnSelect` instead of `Server_Keys_OnSelect`, so the remove button for keys may not refresh correctly. `CreateKey_DlgProc` stores params in a static variable, making concurrent modal instances unsafe even if UI normally prevents them. `ScanServerKey` accepts any three digits after a backslash and truncates to byte, so invalid octal-like values are not rejected. Tests should cover duplicate admin entries, removal of multiple admins, key format round trips, random-key failure disabling, key-version selection, and property-sheet ref-count teardown.
