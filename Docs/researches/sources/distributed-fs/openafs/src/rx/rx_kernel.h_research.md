# Research: sources/distributed-fs/openafs/src/rx/rx_kernel.h

## sources/distributed-fs/openafs/src/rx/rx_kernel.h

### Purpose
`rx_kernel.h` defines RX kernel-client environment mappings for allocation, sockets, sleep/wakeup, panic/assertion, network epoch handling, and interface abstraction.

### Important APIs and Macros
- Maps `osi_Alloc`/`osi_Free` to AFS kernel allocators.
- Defines `osi_socket` as `struct socket *` and `OSI_NULLSOCKET`.
- Maps `osi_rxSleep` and `osi_rxWakeup` to AFS sleep/wakeup tracing wrappers.
- Defines kernel `osi_Panic`/`osi_Assert` variants for Linux, AIX, and other platforms.
- Defines `RX_NET_EPOCH_ENTER`/`RX_NET_EPOCH_EXIT` for FreeBSD epoch-protected network access.
- Abstracts interface types and accessors: `rx_ifnet_t`, `rx_ifaddr_t`, `rx_ifnet_mtu`, `rx_ifnet_flags`, `rx_ifaddr_withnet`, `rx_ifaddr_ifnet`, and address/netmask/dstaddr copy helpers.

### Control Flow and State
The header is macro-driven. It affects how kernel RX code sleeps, wakes, allocates, asserts, enters network epochs, and traverses interface structures. No state is persisted.

### Dependencies and Integration Points
Used by `rx.h` in kernel builds and by kernel RX sources. Integrates with AFS tracing, AFS global lock behavior, kernel socket types, FreeBSD network epochs, and Darwin/BSD interface APIs.

### Risks and Edge Cases
- Macros can evaluate arguments more than once or require surrounding statement care.
- Interface accessors hide platform differences but make compile-time coverage necessary.
- Assertion/panic behavior differs substantially across platforms; Linux uses `BUG()`.
- `rxi_ReScheduleEvents` is defined as `0` in some kernel configurations, so callers must tolerate that.

### Test Signals
Kernel compile coverage and smoke tests for sleep/wakeup, network epoch macros, interface lookup, and assertions under each platform macro set are most relevant.
