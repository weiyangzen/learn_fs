## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_date.h

Purpose: Declares the Date custom control registration function, messages, notifications, and get/set helper macros.

Important APIs and definitions: `RegisterDateClass`, `DM_GETDATE`, `DM_SETDATE`, `DN_CHANGE`, `DN_UPDATE`, `DA_GetDate`, and `DA_SetDate`. Also defines common helper macros `limit`, `inlimit`, `cxRECT`, and `cyRECT` if absent.

Control flow: Header-only message macros send `SYSTEMTIME*` payloads to the Date control; parent notifications are sent as `WM_COMMAND` from implementation.

State and persistence: None in the header. Runtime state is process-local in `ctl_date.cpp`.

Dependencies and integration points: Consumers must create a window of registered class `Date` and pass `SYSTEMTIME` pointers with the macros.

Risks: `DN_CHANGE` is declared but the implementation observed only sends `DN_UPDATE`, so consumers expecting change notifications may not see them. Custom messages use `WM_USER+313/314`, requiring no collision in the control.

Test signals: Compile consumers, verify macro pointer use, and test notification expectations against implementation.
