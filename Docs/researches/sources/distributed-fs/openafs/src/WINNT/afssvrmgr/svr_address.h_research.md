# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_address.h

Purpose: Declares server address change packet and helper APIs.

Important APIs/types: `SVR_CHANGEADDR_PARAMS` contains target server and old/new `SERVERSTATUS`. Exports include address list fill, parse, ping, and `ChangeAddr_DlgProc`.

Control flow/state: Server properties allocate this packet, run the modal dialog, and dispatch address-change task on OK.

Dependencies/integration: Requires server status structures, WinSock address types, and dialog framework.

Risks/test signals: Confirm all users initialize both status snapshots before expecting meaningful diffs.
