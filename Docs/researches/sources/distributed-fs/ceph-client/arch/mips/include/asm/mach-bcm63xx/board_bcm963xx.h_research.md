<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/board_bcm963xx.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/board_bcm963xx.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/board_bcm963xx.h` declares board, firmware, memory, and platform-data contracts for `mach-bcm63xx`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `BOARD_BCM963XX_H_`, `BCM963XX_CFE_VERSION_OFFSET`, `BCM963XX_NVRAM_OFFSET`; 6 structs: `board_info`, `bcm63xx_enet_platform_data`, `bcm63xx_enetsw_platform_data`, `bcm63xx_usbd_platform_data`, `gpio_led`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `board_info`, `bcm63xx_enet_platform_data`, `bcm63xx_enetsw_platform_data`, `bcm63xx_usbd_platform_data`, `gpio_led` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are `linux/types.h`, `linux/gpio.h`, `linux/leds.h`, `bcm63xx_dev_enet.h`, `bcm63xx_dev_usb_usbd.h`. Major macro families are `BCM963XX_CFE (1)`, `BCM963XX_NVRAM (1)`, `BOARD_BCM963XX (1)`. Typed contracts include `board_info`, `bcm63xx_enet_platform_data`, `bcm63xx_enetsw_platform_data`, `bcm63xx_usbd_platform_data`, `gpio_led`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/board_bcm963xx.h -->
