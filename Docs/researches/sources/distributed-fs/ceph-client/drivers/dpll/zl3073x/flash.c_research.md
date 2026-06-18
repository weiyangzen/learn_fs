# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/flash.c

## Purpose
This file implements low-level ZL3073x flash-update operations used by devlink firmware update: entering flash mode, downloading words into device memory, executing flash utility commands, flashing sectors/pages, copying pages, checking utility errors, and returning to normal mode.

## Important APIs and functions
External APIs are `zl3073x_flash_mode_enter()`, `zl3073x_flash_mode_leave()`, `zl3073x_flash_page()`, `zl3073x_flash_page_copy()`, and `zl3073x_flash_sectors()`. Internal helpers include `zl3073x_flash_download()`, `zl3073x_flash_error_check()`, `zl3073x_flash_wait_ready()`, `zl3073x_flash_cmd_wait()`, `zl3073x_flash_get_sector_size()`, `zl3073x_flash_block()`, `zl3073x_flash_mode_verify()`, and `zl3073x_flash_host_ctrl_enable()`.

## Control flow
Flash mode entry sends a fixed hardware-register pre-load sequence, downloads the utility image to RAM at `0x20000000`, sends a post-load sequence to start it, verifies the utility family, enables host control, and reports progress. Flashing a block downloads data to RAM, writes image address/size/page/fill-pattern registers, issues a flash operation, waits for completion, checks utility error counters, and sends devlink progress. Sector flashing chooses 4K or 64K sector size from the utility, splits large firmware into aligned blocks, and advances flash pages by block size. Leave mode sets the reset flag, runs the reset sequence, waits, and checks that reset status cleared.

## State and persistence
This code writes persistent device flash. It also temporarily changes CPU/host-control state and uses device RAM for images. No host-side state persists beyond progress notifications and return codes.

## Dependencies and integration points
It uses `core.c` HWREG and typed register helpers, `regs.h` flash-mode register definitions, and devlink notification wrappers. It is invoked only after normal DPLL operation is stopped by `devlink.c`.

## Risks and edge cases
Flashing can be interrupted by signals during long downloads or waits. Utility command waits can timeout. `zl3073x_flash_mode_leave()` intentionally ignores the reset sequence write error because the device CPU reset makes the last write fail. Incorrect sector size, page math, unaligned component sizes, or failed utility error checks can corrupt updates. Progress uses pointer arithmetic over `void *`, which is accepted by GCC but non-standard C.

## Test signals
Use mocked regmap/HWREG fault injection for pre/post sequences, utility verification failure, host-control failure, sector-size variants, command timeout, utility error count reporting, signal interruption, multi-block sector updates, page copy, and restart after failed flash.
