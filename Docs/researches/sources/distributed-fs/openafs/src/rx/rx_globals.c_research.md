# Research: sources/distributed-fs/openafs/src/rx/rx_globals.c

## sources/distributed-fs/openafs/src/rx/rx_globals.c

### Purpose
`rx_globals.c` instantiates RX global variables by defining `GLOBALSINIT` before including `rx_globals.h`, and implements a small set of runtime tuning accessors.

### Important Functions
- `rx_SetMaxReceiveWindow` and `rx_SetMaxSendWindow` cap requested values at `rx_maxWindow`.
- `rx_GetMaxReceiveWindow` and `rx_GetMaxSendWindow` return current maxima.
- `rx_SetMinPeerTimeout` accepts values in `[1, 999]` milliseconds.
- `rx_GetMinPeerTimeout` returns the minimum peer timeout.
- Windows-only `rx_SetRxDeadTime`, `rx_GetMinUdpBufSize`, and `rx_SetUdpBufSize` provide exported functions where macros are not used.

### Control Flow and State
Including `rx_globals.h` with `GLOBALSINIT(stuff) = stuff` turns the `EXT` declarations into definitions. Setter functions mutate global tuning variables directly. No file or persistent state is written.

### Dependencies and Integration Points
Includes `rx.h`, `rx_clock.h`, `rx_packet.h`, and `rx_globals.h`. The globals are used by nearly every RX subsystem: packet pools, connection/call hashes, service pools, congestion windows, debug output, and thread-specific free packet queues.

### Risks and Edge Cases
- Setters do not enforce lower bounds for send/receive windows.
- Global tuning changes after RX startup can affect existing calls/peers unpredictably.
- The file relies on header macro choreography; including `rx_globals.h` incorrectly can create duplicate definitions or declarations.

### Test Signals
Build/link tests should ensure exactly one definition of globals. Runtime tests should verify window caps, timeout validation, and UDP buffer minimum behavior on Windows.
