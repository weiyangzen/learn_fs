# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/mac.h

## Purpose

`mac.h` declares the low-level MAC, firmware download, queue, FIFO, and DDMA interfaces implemented by `mac.c`, and defines shared constants for MAC port count, firmware memory base addresses, reserved page accounting, and firmware download buffer sizing.

## Important APIs, Types, and Functions

The header defines `RTW_HW_PORT_NUM`, `cut_version_to_mask()`, polling and buffer constants, OCP base addresses for RX buffer, TX buffer, ROM, IMEM, DMEM, and EMEM, and reserved-page counts for driver pages, H2C extra/static info, H2C queue, CPU instruction space, and firmware TX buffer.

It declares channel MAC programming, power sequence parsing, MAC power on/off, firmware page write, firmware download, MAC init/postinit, MAC queue flush, TRX FIFO setup, and DDMA-to-firmware-FIFO transfer. It also provides `rtw_mac_flush_all_queues()` as a helper around `rtw_mac_flush_queues()`.

## Control Flow

The header has no runtime flow; callers use it to invoke the bring-up sequence implemented in `mac.c`. Typical order is power on, firmware download, MAC init, postinit, then runtime queue/channel operations.

## State and Persistence

The constants guide persistent hardware layout and firmware memory transfers. Functions declared here update `rtwdev` flags, FIFO state, H2C state, and hardware registers, but the header itself owns no state.

## Dependencies and Integration Points

`mac.h` is included by core, firmware, debug, and bus code that needs MAC bring-up or queue management. The OCP addresses and reserved page counts must match firmware expectations and chip information tables.

## Risks

Changing shared constants can break firmware download, reserved-page placement, or H2C queue placement across all chips. `cut_version_to_mask()` assumes cut values map cleanly to `1 << (cut + 1)`; new cut encodings would require review.

## Test Signals

Compile tests should catch declaration drift. Runtime tests for all supported buses should verify firmware download addresses, reserved-page boundaries, MAC queue flushing, and channel programming still match hardware expectations after any changes to these constants or prototypes.
