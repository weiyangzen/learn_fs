<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_spec.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_spec.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_spec.h` defines RTL8723B register addresses, queue IDs, page sizes, interrupt masks, firmware command registers, security CAM layout, and SDIO local register constants. The source was reviewed as a complete 237-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `TX_TOTAL_PAGE_NUMBER_8723B`, queue page-boundary constants, `REG_*` aliases, `IMR_*` interrupt bits, `REG_HMEBOX_*`, `REG_HIMR0_8723B`, `REG_HISR0_8723B`, SDIO local offsets, and CAM/security register definitions.

## Control Flow

HAL, SDIO, transmit, receive, interrupt, firmware mailbox, and security code use these constants to read/write the correct MAC, BB, system, and SDIO local registers.

## State and Persistence Behavior

The header defines addresses only; state lives in hardware registers and firmware mailboxes.

## Dependencies and Integration Points

Consumed by almost all RTL8723B-specific `.c` files and descriptor/power/SDIO helpers. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Register aliases are silicon contracts. Incorrect constants can damage unrelated hardware state, mask interrupts, break firmware commands, or corrupt security CAM programming.

## Test Signals

Probe/interrupt smoke tests, H2C/C2H mailbox exercise, TX/RX queue operation, security association, and register dump comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_spec.h -->
