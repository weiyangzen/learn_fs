# sources/distributed-fs/ceph-client/drivers/mmc/host/mvsdio.h Research

## sources/distributed-fs/ceph-client/drivers/mmc/host/mvsdio.h

### Purpose
`mvsdio.h` defines the private Marvell Orion SDIO/MMC controller register map and bitfields consumed by `mvsdio.c`. It is a hardware contract rather than executable logic, covering clock limits, command/transfer/host-control encoding, interrupt status/error bits, auto-CMD12 status, DMA/window registers, and reset/control offsets.

### Important APIs, Types, And Functions
There are no functions or C types beyond preprocessor constants. Important groups are register offsets such as `MVSD_SYS_ADDR_LOW`, `MVSD_BLK_SIZE`, `MVSD_CMD`, `MVSD_FIFO`, `MVSD_HOST_CTRL`, `MVSD_CLK_DIV`, interrupt enable/status registers, auto-CMD12 registers, and MBUS window registers. Bitfield groups define command response types and CRC/index checks, transfer-mode flags for write start, hardware write data, auto-CMD12, interrupt checking, read direction, stop clock, and PIO, host-control flags for push-pull, card type, endian/bit order, 4-bit width, high-speed, and timeout, normal interrupt bits, error bits, and auto-CMD12 error bits.

### Control Flow
The header has no control flow. `mvsdio.c` composes these constants into request-time command registers, transfer modes, interrupt masks, host-control settings, clock divisors, reset operations, DMA address programming, and error decoding.

### State, Persistence, And Dependencies
The persistent state represented by these constants lives in hardware registers. `mvsdio.c` caches selected values (`xfer_mode`, `intr_en`, `ctrl`) and writes them back using these definitions. The header depends only on inclusion by C code that provides standard integer/register access helpers; it uses no Linux types itself.

### Integration Points
This file is tightly coupled to `mvsdio.c` and the Marvell controller documentation. It also supports MBUS integration through `MVSD_WINDOW_CTRL()` and `MVSD_WINDOW_BASE()` macros, allowing `mvsdio.c` to program DRAM decode windows before DMA.

### Risks
Any incorrect offset or bit definition directly misprograms hardware. Timeout mask/index fields, response reconstruction assumptions, PIO/DMA transfer-mode bits, and normal/error interrupt masks are especially high impact because the driver uses them to decide request completion and error propagation. The header does not enforce field widths; callers must clamp divisors, timeout indices, and command indices correctly.

### Test Signals
Validation comes from exercising every consumer path in `mvsdio.c`: response types, auto-CMD12, PIO and DMA, SDIO interrupts, reset, timeout programming, 4-bit bus, push-pull/open-drain, MBUS windows, and all command/data/auto-CMD12 error statuses. Register dumps during known-good transfers are useful for comparing encoded constants against hardware documentation.
