# sources/distributed-fs/ceph-client/drivers/remoteproc/mtk_scp_ipi.c

## Purpose

`mtk_scp_ipi.c` provides the exported Inter-Processor Interrupt API used by MediaTek SCP client drivers and the MediaTek rpmsg bridge. It registers per-IPI handlers, copies data into the shared SCP SRAM object with alignment-safe writes, sends host-to-SCP interrupts, and optionally waits for firmware acknowledgements.

## Important APIs, types, and functions

- `scp_ipi_register()` installs a handler and private pointer for an IPI id.
- `scp_ipi_unregister()` clears the handler and private pointer.
- `scp_memcpy_aligned()` writes to SCP SRAM using 32-bit writes and read-modify-write at unaligned edges because byte writes are not supported.
- `scp_ipi_lock()` and `scp_ipi_unlock()` expose per-IPI mutexes for the SCP core driver.
- `scp_ipi_send()` validates id/length/buffer, enables the SCP clock, serializes sends with `send_lock`, waits for the previous host-to-SCP register to clear, writes payload/id/len to `send_buf`, triggers the configured IPC bit, optionally waits for `ipi_id_ack[id]`, and disables the clock.

## Control flow

Clients register handlers after obtaining an `mtk_scp`. Sending an IPI first validates that the id is not reserved (`SCP_IPI_INIT`, `SCP_IPI_NS_SERVICE`, or out of range), that the buffer fits the SoC's `ipi_share_buffer_size`, and that a buffer exists. It enables the SCP clock, waits up to `SCP_TIMEOUT_US` for the host IPC register to be idle, copies payload into shared SRAM, writes length and id, clears the ack flag, triggers the host-to-SCP bit, and optionally waits for the core interrupt path to set the ack flag.

Inbound dispatch itself lives in `mtk_scp.c`; this file supplies the locking and send-side API it uses.

## State and persistence behavior

Handler state persists in `scp->ipi_desc[id]` until unregistered. Send-side serialization is per SCP instance through `send_lock`. Ack state is stored in `ipi_id_ack[]` and `ack_wq`. Hardware-visible state is the shared SRAM `send_buf` object and host-to-SCP IPC register bit; both are overwritten on each send.

## Dependencies and integration points

The file depends on `mtk_common.h`, the public `linux/remoteproc/mtk_scp.h` IPI ids and handler types, clocks, IO accessors, atomic polling, and waitqueues. It exports all APIs with GPL symbols for MediaTek media/rpmsg clients.

## Risks and edge cases

- `scp_ipi_send()` assumes `scp`, `scp->data`, `scp->send_buf`, and `scp->clk` are valid; unlike register/unregister it does not guard against NULL `scp`.
- The wait parameter is in milliseconds; a zero wait sends fire-and-forget and does not prove firmware accepted the command.
- `scp_memcpy_aligned()` may write extra bytes at the beginning and end of the destination word, intentionally preserving existing bytes by reading first. Concurrent writers to overlapping words would be unsafe.
- Timeout while waiting for the host IPC register leaves the previous SCP command state unresolved and returns without sending the new message.
- Ack flags are indexed by IPI id, so clients must avoid sharing an id concurrently beyond the provided `send_lock` serialization.

## Test signals

Unit-style tests should cover invalid ids, NULL handlers, oversize messages, unaligned destination copies, timeout when host IPC never clears, fire-and-forget sends, waited sends with ack, unregister during no active dispatch, and clock enable failures. Integration tests should verify IPI namespace service, rpmsg channel creation, and client media capability exchanges.
