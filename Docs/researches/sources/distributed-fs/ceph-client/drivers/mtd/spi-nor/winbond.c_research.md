# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/winbond.c

## Purpose
Provides Winbond SPI NOR manufacturer support, including a large Winbond part table, SFDP corrections, multi-die readiness handling, extended address register cleanup, and Winbond OTP operation wiring.

## Important APIs, Types, and Functions
The exported manufacturer is `spi_nor_winbond`. `winbond_nor_parts[]` records W25X/W25Q/W25M/W25H variants, feature flags, fallback no-SFDP capabilities, and OTP layouts. Fixups include `w25q128_post_bfpt_fixups()` for a Zetta clone with incorrect SFDP size, `w25q256_post_bfpt_fixups()` to distinguish W25Q256JV 4-byte opcodes, and `winbond_nor_multi_die_post_sfdp_fixups()` to install multi-die status polling. `winbond_nor_set_4byte_addr_mode()` wraps generic EN4B/EX4B and clears EAR on exit through `winbond_nor_write_ear()`. `winbond_nor_otp_ops` maps to security-register OTP helpers.

## Control Flow
After matching a part, BFPT fixups patch size or 4-byte opcode flags. Multi-die parts compute `n_dice` from capacity and replace the ready callback with `winbond_nor_multi_die_ready()`, which selects each die and polls status. Late init installs OTP ops when an OTP organization exists and always overrides the set-4-byte-address-mode callback with the Winbond-specific wrapper.

## State and Persistence
The file mutates runtime params (`n_dice`, `ready`, `otp.ops`, `set_4byte_addr_mode`) and may write persistent/volatile device registers: die select, EN4B/EX4B, and the Extended Address Register. Clearing EAR after leaving 4-byte mode avoids stale high-address reads in subsequent 3-byte mode.

## Dependencies and Integration Points
It depends on `spi_mem` operation construction, SPI NOR core read/write register helpers, OTP security register helpers, and BFPT/SFDP parse callbacks. It integrates through the manufacturer table consumed by the SPI NOR core.

## Risks
Several Winbond variants share JEDEC IDs, so SFDP version heuristics are used to distinguish behavior. Multi-die readiness depends on die-select command support and a correct dice count. Clearing EAR requires write enable and write disable; failure can leave 3-byte reads mapped to the wrong 16 MiB window.

## Test Signals
Probe representative Winbond devices, especially W25Q128 clone, W25Q256FV/JV, and multi-die W25Q01/W25Q02 parts. Validate 4-byte exit followed by low-address 3-byte reads, OTP read/write/lock behavior, and die-by-die ready polling during long erase/program operations.
