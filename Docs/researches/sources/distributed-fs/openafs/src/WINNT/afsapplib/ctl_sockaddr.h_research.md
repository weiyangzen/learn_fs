## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_sockaddr.h

Purpose: Declares the socket-address custom control interface.

Important APIs and definitions: `RegisterSockAddrClass`, messages `SAM_GETADDR` and `SAM_SETADDR`, notifications `SAN_CHANGE` and `SAN_UPDATE`, plus `SA_GetAddr` and `SA_SetAddr` macros. It also conditionally defines common geometry/limit macros.

Control flow: Header macros send `SOCKADDR_IN*` payloads to the control. Notifications return through parent `WM_COMMAND` with `LPARAM` pointing to a `SOCKADDR_IN`.

State and persistence: None in the header; runtime state is held by `ctl_sockaddr.cpp`.

Dependencies and integration points: Consumers must include Winsock-compatible definitions before using `SOCKADDR_IN` payloads, and create a registered `SockAddr` class control.

Risks: Notification comment for `SAN_CHANGE` says `SOCKADDR_IN *pTime`, a copy-paste typo that can mislead maintainers. Custom messages may collide if sent to the wrong window class.

Test signals: Compile with Winsock headers, get/set macros, parent notification payload handling, and class registration before dialog creation.
