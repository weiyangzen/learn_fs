# sources/distributed-fs/ceph-client/drivers/firmware/broadcom/bcm47xx_nvram.c

## Purpose
This file provides early Broadcom bcm47xx-style NVRAM access. It locates a flash NVRAM blob, copies it into a static RAM buffer, and exports simple lookup helpers for `name=value` variables, GPIO aliases, and full contents.

## Important APIs, Types, And Functions
`struct nvram_header` describes the flash header with magic `FLSH`, length, and SDRAM fields. `nvram_buf[NVRAM_SPACE]` and `nvram_len` are the global cached copy. Initialization paths are `bcm47xx_nvram_init_from_iomem()` for a known mapped NVRAM start, `bcm47xx_nvram_init_from_mem()` for an early physical flash window, and internal `nvram_init()` for an MTD partition named `nvram`.

Lookup APIs are `bcm47xx_nvram_getenv()`, `bcm47xx_nvram_gpio_pin()`, and `bcm47xx_nvram_get_contents()`. `bcm47xx_nvram_find_and_copy()` scans likely NVRAM locations at flash-size ends plus 4 KiB/1 KiB embedded fallbacks. `bcm47xx_nvram_copy()` bounds the header length to the backing resource and static buffer.

## Control Flow, State, And Persistence
The first successful initialization persists data in `nvram_buf` for the life of the kernel. Reinitialization returns `-EEXIST`. Consumers can call lookup functions without explicit initialization; they lazily call `nvram_init()`, which uses MTD when available. Variables are parsed by walking null-terminated strings after the header until an empty entry or buffer end.

## Dependencies And Integration Points
The file depends on IO mapping, MTD reads, `linux/bcm47xx_nvram.h`, and exported GPL/non-GPL symbols used by board, SPROM, and platform code. It intentionally supports very early calls before normal platform devices are available.

## Risks And Test Signals
Risks include trusting flash header length, scanning false-positive magic values, lazy MTD availability, and global unsynchronized initialization. The code clamps oversize copies and null-terminates the buffer, but does not validate CRC. Test signals are direct iomem init with valid/invalid magic, flash scanning offsets, duplicate init, MTD fallback, getenv exact-name matching, GPIO search over `gpio0`..`gpio31`, and contents allocation length.
