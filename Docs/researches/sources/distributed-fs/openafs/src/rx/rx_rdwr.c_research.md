# sources/distributed-fs/openafs/src/rx/rx_rdwr.c

## Purpose
Implements RX call stream read/write APIs over packet queues. It translates application byte streams and iovecs into ordered RX data packets, handles receive queue consumption and hard ACK scheduling, manages transmit-window waits, and flushes final packets.

## Important APIs, Types, And Functions
Important functions are `rxi_GetNextPacket`, `rxi_ReadProc`, `rx_ReadProc`, `rx_ReadProc32`, `rxi_FillReadVec`, `rxi_ReadvProc`, `rx_ReadvProc`, `rxi_WriteProc`, `rx_WriteProc`, `rx_WriteProc32`, `rx_WritevAlloc`, `rxi_WritevProc`, `rx_WritevProc`, `rxi_FlushWrite`, `rxi_FlushWriteLocked`, and `rx_FlushWrite`. The file manipulates `struct rx_call` fields including `rq`, `tq`, `app.currentPacket`, `app.curvec`, `app.curpos`, `app.curlen`, `app.nLeft`, `app.nFree`, `app.mode`, `app.iovq`, `rnext`, `tnext`, `tfirst`, `twind`, `nHardAcks`, `flags`, and call condition variables.

## Control Flow
Reads first free any previously loaned iovec packets. If no current packet has data, `rxi_GetNextPacket` removes the next in-sequence packet from `rq`, checks it with the connection security class, advances `rnext`, initializes application cursor fields, and increments hard ACK accounting. Scalar reads copy bytes to caller buffers and free packets as they are exhausted. Vector reads fill caller iovecs with direct pointers into packet buffers, move exhausted packets into `app.iovq` so they stay alive until the next read/write call, and wait on `cv_rq` when more data is needed.

Writes switch server calls from receive to send mode when legal, allocate send packets sized by MTU and security overhead, copy bytes into packet iovecs, extend packets with continuation buffers when useful, prepare full packets with `rxi_PrepareSendPacket`, append them to the transmit queue, and start transmission unless fast recovery is active. Vector writes split into allocation (`rx_WritevAlloc`, which gives the application direct packet-buffer iovecs) and commit (`rx_WritevProc`, which validates the returned iovecs, adjusts cursors, queues full packets, and handles protocol errors). Flush sends a final packet, possibly zero-length, marks it with `RX_LAST_PACKET`, and transitions clients to receiving or servers to EOF.

## State And Persistence
All state is in-memory per call. The file persists stream position across API calls through `call->app` fields and holds packet buffers in `currentPacket`, `rq`, `tq`, and `iovq`. It also updates per-call byte counters, hard ACK counters, wait timestamps, mode flags, and error state.

## Dependencies And Integration Points
It depends on packet allocation/freeing, security-class packet checks/preparation, ACK scheduling, retransmit start logic, call locks/CVs, RX clock, and connection state. It is used by generated RX stubs and application code through `rx_ReadProc*`, `rx_WriteProc*`, vector APIs, and flush.

## Risks And Test Signals
Risks include deadlocks around call lock drops in `rxi_PrepareSendPacket`, packet lifetime bugs with `iovq`, off-by-one iovec cursor logic, returning 0 on errors without preserving partial-byte semantics, transmit-window wait starvation, and protocol errors when applications alter allocated iovecs. Test signals include scalar and vector RPCs, zero-length responses, fragmented large replies, security check failures, lost packet/retransmit recovery, hard ACK scheduling, and concurrent client/server mode transitions.
