# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-tx.c

Purpose: Implements MCP251xFD transmit path from SocketCAN SKB to controller TX RAM load and FIFO request-to-send.

Important APIs, types, and functions: `mcp251xfd_start_xmit()` is the netdev TX entry; `mcp251xfd_tx_obj_write_sync()` is the workqueue fallback. Helpers choose the next TX object, convert SKB fields into hardware ID/flags/data, compute optional CRC and transfer length, detect ring fullness, and roll back failed submissions.

Control flow: Start-xmit rejects invalid SKBs, checks ring/free work state, builds a TX object with sequence number equal to software head, stops queue if FIFO becomes full, stores echo SKB and accounting, then submits the SPI message asynchronously. `-EBUSY` queues synchronous work; other errors drop and roll back.

State and persistence behavior: Mutates TX head, pending work object, echo SKB slots, and netdev queue accounting. TEF completion advances tail.

Dependencies and integration points: Depends on CAN/CAN-FD SKB helpers, SPI async/sync APIs, CRC helper, ring prebuilt messages, and TEF sequence validation.

Risks: TX and TEF must agree on sequence masks. The fallback has a single pending work object. Padding, sanitization, and CRC length calculations must match RAM command semantics.

Test signals: Standard/extended/RTR/CAN-FD/BRS/ESI transmit, full FIFO stop, TEF wakeup, SPI `-EBUSY` fallback, hard error rollback, echo accounting, and CAN FD length sanitization.
