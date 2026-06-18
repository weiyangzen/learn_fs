<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops_linux.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops_linux.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops_linux.h` declares the Linux SDIO bus backend for CMD52/CMD53-style byte, word, dword, memory, and port access. The source was reviewed as a complete 30-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `sd_cmd52_read`, `sd_cmd52_write`, `sd_read8`, `sd_read32`, `sd_read`, `sd_write8`, `sd_write32`, `_sd_write`, `sd_write`, and `rtw_sdio_set_irq_thd`.

## Control Flow

Generic SDIO ops dispatch here to perform Linux kernel SDIO transfers and manage the SDIO interrupt thread handle.

## State and Persistence Behavior

Uses Linux `sdio_func`/interface state behind `intf_hdl` and stores the IRQ thread handle in `dvobj_priv`.

## Dependencies and Integration Points

Depends on Linux MMC/SDIO APIs, `struct intf_hdl`, and `struct dvobj_priv`. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Bus transfer failures, alignment, and host-claiming rules are critical. IRQ thread handle lifetime must track device removal.

## Test Signals

CMD52/CMD53 transfer tests, SDIO interrupt registration/removal, transfer error injection, and suspend/resume with IRQ enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_ops_linux.h -->
