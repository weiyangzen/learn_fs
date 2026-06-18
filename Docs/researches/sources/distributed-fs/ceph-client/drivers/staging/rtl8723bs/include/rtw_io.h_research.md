<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_io.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_io.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_io.h` defines the generic IO abstraction around `intf_hdl`, synchronous/asynchronous memory/register operations, and bus-specific IO operation callbacks. The source was reviewed as a complete 74-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct intf_hdl`, `struct _io_ops`, `rtw_read8`, `rtw_read16`, `rtw_read32`, `rtw_write8`, `rtw_write16`, `rtw_write32`, `rtw_read_mem`, `rtw_write_mem`, `rtw_write_port`, `rtw_read_port`, `rtw_init_io_priv`, and `register_intf_hdl`.

## Control Flow

HAL and data-path code call generic IO helpers; the interface handle dispatches to SDIO-specific operations from `sdio_ops.h`/`sdio_ops_linux.h`.

## State and Persistence Behavior

`intf_hdl` binds adapter/dvobj context to the selected IO callback table; hardware state changes through the actual bus operations.

## Dependencies and Integration Points

Connected to SDIO ops, HAL register access, transmit/receive port IO, and Linux SDIO bus glue. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Wrong callback registration or address translation affects every register and FIFO access. Error propagation must be observed by callers.

## Test Signals

Register read/write smoke, memory and port IO, SDIO error injection, and probe/unload IO handle lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_io.h -->
