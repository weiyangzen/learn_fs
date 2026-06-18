# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_address.cpp

Purpose: Implements server address display, parsing, host lookup, and the Change Addresses dialog used by server properties.

Important APIs/functions: `Server_FillAddrList` populates address listbox from `SERVERSTATUS`. `Server_ParseAddress` converts text to `SOCKADDR_IN` using `inet_addr`. `Server_Ping` resolves a server hostname with `gethostbyname`. `ChangeAddr_DlgProc` handles address edit UI. `ChangeAddr_OnEndTask_Init` loads old/new `SERVERSTATUS` from `taskSVR_PROP_INIT`. `ChangeAddr_OnRemove` zeroes selected address entries. `ChangeAddr_OnChange` opens `NewAddr_DlgProc` and updates `ssNew`.

Control flow: The dialog starts disabled with a querying list, runs server property init, copies status into old/new structures, then lets the user remove/change addresses. Change operation prevents duplicates by detecting an existing new address and converting the selected old address to zero instead.

State and persistence: `SVR_CHANGEADDR_PARAMS` stores server identity plus old/new status snapshots. The dialog mutates `ssNew`; on OK the caller starts `taskSVR_CHANGEADDR`. No registry/local persistence.

Dependencies/integration: Uses WinSock, AFS address conversion helpers, listbox helpers, server property task data, and socket-address UI control helpers `SA_SetAddr/SA_GetAddr`.

Risks: `inet_addr` error value for invalid input is not validated distinctly from broadcast-like values. `Server_Ping` uses legacy `gethostbyname`, IPv4 only, and broad catch. Address removal loops over `ssOld.nAddresses` and indexes `ssNew` by same count, assuming arrays match. Zero-address entries are hidden, so user cannot directly re-add through this dialog.

Test signals: Server with no addresses, multiple addresses, duplicate replacement, remove all, invalid address text through new address control, failed property init, and host lookup failure.
