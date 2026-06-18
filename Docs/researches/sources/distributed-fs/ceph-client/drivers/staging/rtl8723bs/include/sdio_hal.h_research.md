<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_hal.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_hal.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_hal.h` declares SDIO-specific HAL operation setup for RTL8723BS. The source was reviewed as a complete 14-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtl8723bs_set_hal_ops`.

## Control Flow

During bus-specific probe, SDIO code installs chip HAL callbacks so generic `rtw_hal_*` calls dispatch to RTL8723BS SDIO implementations.

## State and Persistence Behavior

Mutates adapter HAL operation tables during initialization.

## Dependencies and Integration Points

Integrates with `rtl8723b_hal.h`, `hal_intf.h`, SDIO bus probe, and `sdio_ops.h`. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

If operations are not installed before generic HAL calls, initialization or TX/RX paths will dereference missing callbacks.

## Test Signals

Probe path ordering, HAL init/deinit through SDIO, and all generic HAL operations after ops installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/sdio_hal.h -->
