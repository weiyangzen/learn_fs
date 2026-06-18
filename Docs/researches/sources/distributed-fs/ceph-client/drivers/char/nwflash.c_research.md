# sources/distributed-fs/ceph-client/drivers/char/nwflash.c

## Purpose
`nwflash.c` implements a misc character device for the Intel flash chips used on NetWinder systems. It exposes flash ROM contents via `/dev/nwflash`, supports reads and guarded writes/erases, detects 1 MiB versus 4 MiB flash IDs, and directly controls board-specific write-enable hardware.

## Important APIs, Types, and Functions
- `get_flash_id()` maps flash commands through `FLASH_BASE`, reads the vendor/device ID, restores read mode, and sets `gbFlashSize` for 4 MiB parts.
- `flash_ioctl()` accepts `CMD_WRITE_DISABLE`, `CMD_WRITE_ENABLE`, and `CMD_WRITE_BASE64K_ENABLE` to control global write gates.
- `flash_read()` uses `simple_read_from_buffer()` under `nwflash_mutex`.
- `flash_write()` validates write enable, blocks writes to the first 64 KiB unless explicitly enabled, clamps to flash size, erases affected 64 KiB blocks, programs data with `write_block()`, and updates `*ppos`.
- `erase_block()` sends Intel erase commands, polls status with a 10-second timeout, restores read mode, and verifies erased words.
- `write_block()` programs bytes one by one through the Footbridge ROM write register and verifies the written data.
- `kick_open()` toggles NetWinder CPLD flash write-enable bits under `nw_gpio_lock`.

## Control Flow
Init only proceeds on `machine_is_netwinder()`. It maps `DC21285_FLASH`, verifies the flash ID, logs size, and registers `NWFLASH_MINOR`. Users must enable writes via ioctl before write calls. A write computes the affected 64 KiB block range, erases each block with retries, programs up to the end of the block, retries full erase/write on verify failure, and stops on error or completion.

## State and Persistence
The hardware flash is persistent boot firmware storage. Software state includes mapped `FLASH_BASE`, detected `gbFlashSize`, write-enable flags, `flashdebug`, `flash_mutex`, and `nwflash_mutex`. Writes are destructive because whole blocks are erased before programming.

## Dependencies and Integration Points
The driver is ARM NetWinder-specific. It depends on Footbridge registers (`CSR_ROMWRITEREG`), `DC21285_FLASH`, NetWinder CPLD/GPIO helpers, misc core, board machine detection, and ioctl constants from `asm/nwflash.h`.

## Risks
- The source warns writes can render the machine unbootable; the first 64 KiB has an additional write gate.
- Write-enable flags are global rather than per-open, so one process can enable writes for another.
- Erase/program timeouts, byte programming, and verify loops directly affect firmware integrity.
- Pointer arithmetic casts MMIO pointers through `unsigned int`, making this code architecture-bound.

## Test Signals
Testing should prefer hardware simulation or read-only smoke tests. Signals include correct refusal on non-NetWinder systems, ID detection for both flash IDs, read bounds behavior, ioctl gating for normal and base-64K writes, erase/program retry logging, and successful verify after writes on sacrificial hardware.
