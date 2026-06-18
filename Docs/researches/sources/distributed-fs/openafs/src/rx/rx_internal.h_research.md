# Research: sources/distributed-fs/openafs/src/rx/rx_internal.h

## sources/distributed-fs/openafs/src/rx/rx_internal.h

### Purpose
`rx_internal.h` declares RX-private globals and functions that should not be exposed to ordinary RX library callers.

### Important APIs and State
- Private globals: `rx_nWaiting`, `rx_nWaited`, and `rx_host`.
- Defines `RXI_SENDMSG_RETRY` for error-queue send retry behavior.
- Declares internal functions from `rx.c`: running checks, delayed ACK cancellation/posting, packet wait wakeup, peer MTU updates, network error handling, peer lookup, packet receive dispatch, connection interestingness, connection/call errors, send/start/ack/abort helpers, RPC stats increment, TQ busy wait, and local address retrieval.
- Declares packet helpers: `rxi_SplitJumboPacket` and `rxi_GetLocalSpecialPacket`.
- Declares `osi_Msg` for applicable platforms.

### Control Flow and Integration
This header is a cross-file linkage contract. Receive loops in LWP/kernel paths call `rxi_ReceivePacket`; event callbacks call delayed ACK/abort/send helpers; packet and network layers call MTU and error handlers.

### State and Persistence
Only in-memory RX runtime state is referenced. No durable persistence.

### Dependencies and Integration Points
Conditionally includes Linux error-queue headers for `AFS_RXERRQ_ENV`. It is consumed by RX implementation files such as `rx_call.c`, `rx_lwp.c`, `rx_kcommon.c`, packet code, and platform socket paths.

### Risks and Edge Cases
- Internal prototypes are broad and tightly coupled to `rx.c`; signature drift breaks multiple platform paths.
- Error-queue support depends on Linux-specific types and must stay guarded.
- Callers of these functions usually need specific locks or refcounts that are not encoded in the type signatures.

### Test Signals
Build coverage with and without `AFS_RXERRQ_ENV`, kernel/user-space variants, and network error integration tests are key.
