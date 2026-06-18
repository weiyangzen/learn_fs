## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_sockaddr.cpp

Purpose: Implements a composite IPv4 socket-address entry control made of four numeric edit fields separated by dots.

Important APIs and functions: `RegisterSockAddrClass` registers class `SockAddr`. `SockAddrProc` handles lifecycle, focus, enable, click forwarding, and `SAM_GETADDR`/`SAM_SETADDR`. `SockAddr_OnCreate` builds child fields. `SockAddrDlgProc` routes edit notifications. `SockAddrEditProc` handles dot key focus advance and kill-focus formatting. Edit helpers synchronize `SOCKADDR_IN`.

Control flow: On creation the placeholder creates four child edit controls and static separators in the parent dialog, subclasses each edit, and initializes address to zero. `EN_CHANGE` clamps octets, updates `sin_addr` byte fields, sends `SAN_CHANGE` with a mutable copy, and applies any parent-modified address. `EN_UPDATE` sends `SAN_UPDATE`.

State and persistence: Global `aSockAddr` table guarded by `csSockAddr` maps placeholder HWNDs to child HWNDs and current `SOCKADDR_IN`. No persistence.

Dependencies and integration points: Uses Winsock2 `SOCKADDR_IN`, `dialog.h`, `resize.h`, `subclass.h`, locale helpers, and public macros in `ctl_sockaddr.h`.

Risks: Uses legacy `sin_addr.s_net/s_host/s_lh/s_impno` byte fields, which are non-portable and depend on Windows layout. First octet is clamped 1-253 after entry begins, while all-zero is used as the blank sentinel. Parent color handler creates brushes without cleanup. No port/family validation is performed.

Test signals: Blank address, setting/getting addresses, first-octet min/max, other octet 0-255 limits, dot key navigation, parent modification in `SAN_CHANGE`, kill-focus formatting, disabled state, and byte-order expectations.
