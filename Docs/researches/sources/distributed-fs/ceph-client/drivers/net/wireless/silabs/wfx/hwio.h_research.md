# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hwio.h

Purpose: Declares WFx low-level I/O APIs and register bit definitions for config, control, and IGPR access.

Important APIs and types: Exports data queue read/write, SRAM/AHB buffer and register helpers, config/control register helpers, and IGPR read/write. Defines config error bits, byte order/direct-access/prefetch/reset/IRQ/clock/device ID bits, control next-length/wakeup/ready bits, and IGPR field masks.

Control flow and integration: BH uses data/control/config helpers; firmware loading uses SRAM/IGPR/config/control helpers; bus drivers supply the backend operations.

State and persistence: Header constants describe device register state. Callers must provide DMA-safe kmalloc buffers for data and indirect I/O.

Dependencies: Depends on Linux types and WFx bus abstraction at implementation sites.

Risks and test signals: Risks include misuse of stack buffers, confusing SPI/SDIO-specific config error bits, and incorrect `CTRL_NEXT_LEN_MASK` handling. Tests should enable DMA debugging, validate register bit masks, and exercise both bus backends.

Test signals: Source read size: 78 lines, 3402 bytes.
