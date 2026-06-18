<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops.h` declares SDIO register, FIFO, and initialization operations at the Realtek IO abstraction layer. The source was reviewed as a complete 34-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `sdio_init`, `sdio_deinit`, `sdio_read8`, `sdio_read16`, `sdio_read32`, `sdio_write8`, `sdio_write16`, `sdio_write32`, `sdio_read_mem`, `sdio_write_mem`, `sdio_read_port`, `sdio_write_port`, `sdio_set_intf_ops`, and address translation helpers.

## Control Flow

IO abstraction and HAL code call SDIO operations to access MAC/SDIO local registers and data ports; initialization binds these operations into `intf_hdl`.

## State and Persistence Behavior

The operations affect hardware registers/FIFOs and SDIO device-object state, but this header owns no storage.

## Dependencies and Integration Points

Backed by Linux SDIO implementations in `sdio_ops_linux.h` and used by `rtw_io.h`, `hal_sdio.h`, transmit, receive, and interrupt handling. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Address translation and port lengths must match SDIO block size and hardware alignment. Error pointers must propagate to callers.

## Test Signals

SDIO register read/write, block/byte mode transfer, RX/TX port operations, interrupt path, and probe/remove loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops.h -->
