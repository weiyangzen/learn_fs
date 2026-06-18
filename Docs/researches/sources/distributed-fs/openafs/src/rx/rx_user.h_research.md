# sources/distributed-fs/openafs/src/rx/rx_user.h

## Purpose
Defines user-mode RX platform macros and socket/allocator abstractions.

## Important APIs, Types, And Functions
The header defines no-op priority/GLOCK macros (`SPLVAR`, `NETPRI`, `USERPRI`, `AFS_GLOCK`, `AFS_GUNLOCK`, `AFS_ASSERT_GLOCK`, `ISAFS_GLOCK`), `osi_socket` and `OSI_NULLSOCKET` for UAFS, Windows, and Unix, sleep/wakeup macros, allocation/free macros, `osi_GetTime`, and `osi_Assert`.

## Control Flow
No runtime flow exists. The macros let shared RX code compile in user mode without kernel priority or global-lock operations.

## State And Persistence
No state is stored. The socket typedef determines how socket values are represented by user-mode code.

## Dependencies And Integration Points
It includes AFS parameters, standard C allocation headers, and LWP headers. `rx_packet.c`, `rx_user.c`, and user-mode transport code include it to bridge platform differences.

## Risks And Test Signals
Risks include mismatched socket type assumptions, allocator macro conflicts, and accidentally relying on no-op lock/priority macros in code later used in kernel builds. Cross-platform user-mode builds and basic socket tests are the main signals.
