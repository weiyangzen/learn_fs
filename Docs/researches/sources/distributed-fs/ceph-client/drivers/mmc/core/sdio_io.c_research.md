# sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_io.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_io.c

### Purpose
`sdio_io.c` provides the exported SDIO function-driver API for claiming the host, enabling/disabling functions, setting block size, doing CMD52/CMD53 I/O, querying PM capabilities, setting suspend flags, and managing retuning around SDIO transactions.

### Important APIs, Types, And Functions
Exports include `sdio_claim_host()`, `sdio_release_host()`, `sdio_enable_func()`, `sdio_disable_func()`, `sdio_set_block_size()`, `sdio_align_size()`, `sdio_readb()`, `sdio_writeb()`, `sdio_writeb_readb()`, `sdio_memcpy_fromio()`, `sdio_memcpy_toio()`, `sdio_readsb()`, `sdio_writesb()`, `sdio_readw()`, `sdio_writew()`, `sdio_readl()`, `sdio_writel()`, `sdio_f0_readb()`, `sdio_f0_writeb()`, `sdio_get_host_pm_caps()`, `sdio_set_host_pm_flags()`, `sdio_retune_crc_disable()`, `sdio_retune_crc_enable()`, `sdio_retune_hold_now()`, and `sdio_retune_release()`. Internal helpers include `sdio_max_byte_size()`, `_sdio_align_size()`, and `sdio_io_rw_ext_helper()`.

### Control Flow
Function enable sets the function bit in `IOEx`, then polls `IORx` until ready or `func->enable_timeout`. Block size writes low/high FBR block-size bytes and updates `func->cur_blksize`. Bulk transfer helper chooses block mode when multi-block is supported and the transfer exceeds byte-mode limits, splits at host/card limits, then writes the remainder in byte mode; FIFO helpers use fixed address while memcpy helpers increment the address. Scalar 16/32-bit helpers marshal through `func->tmpbuf` in little-endian form. F0 writes are restricted to vendor CCCR range unless a card quirk allows lenient writes.

### State, Persistence, And Dependencies
State changes include function enable bits, FBR block-size registers, `func->cur_blksize`, host PM flags, host retune suppression fields, and card/host command state. Dependencies include SDIO ops CMD52/CMD53 helpers, MMC host/card structures, retune helpers, card quirks, and exported GPL symbols for function drivers.

### Integration Points
All SDIO function drivers depend on this API after binding through `sdio_bus.c`. `sdio_bus_probe()` uses `sdio_set_block_size()` before calling driver probe. `sdio_uart.c` uses claim/release, scalar I/O, enable/disable, and IRQ helpers.

### Risks
Most APIs assume the caller has claimed the host where documented; misuse can race with other functions or PM. `sdio_writeb_readb()` does not guard `func == NULL` unlike `sdio_readb()`/`sdio_writeb()`. `func->tmpbuf` serializes 16/32-bit helpers per function only if callers respect host claiming. Transfer splitting must honor `max_blk_count`, `max_blk_size`, multi-block support, byte-mode 512 quirks, and address-increment semantics. PM flags are ORed without locking based on serialized suspend callbacks.

### Test Signals
Exercise enable timeout, disable, default/custom block sizes, byte-mode 512 quirk, multi-block CMD53 splitting, FIFO versus incrementing address transfers, 8/16/32-bit endian reads/writes, F0 vendor-range enforcement, PM flag validation, and retune hold/CRC disable around noisy power-state transitions.
