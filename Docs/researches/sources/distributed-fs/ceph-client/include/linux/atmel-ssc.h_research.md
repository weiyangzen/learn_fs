# sources/distributed-fs/ceph-client/include/linux/atmel-ssc.h

## Purpose
Defines platform data, shared device structure, request/free API, register offsets, bitfield constants, PDC offsets, and access macros for Atmel Synchronous Serial Controller devices.

## Important APIs, Types, And Functions
`struct atmel_ssc_platform_data` describes DMA usage and extended frame-sync length support. `struct ssc_device` stores list linkage, physical base, mapped registers, platform device, platform data, clock, user count, IRQ, RK-pin clock flag, and sound DAI flag. APIs are `ssc_request()` and `ssc_free()`. Register definitions cover control, clock mode, RX/TX clock/frame modes, hold/sync/compare registers, status, interrupt enable/disable/mask, and PDC pointer/counter/control/status registers. Bitfield helpers `SSC_BIT()`, `SSC_BF()`, `SSC_BFEXT()`, and `SSC_BFINS()` construct/extract/insert fields. `ssc_readl()` and `ssc_writel()` perform raw MMIO access by symbolic register name.

## Control Flow, State, And Persistence
SSC users request a shared controller, configure clock/frame registers, enable RX/TX, manage interrupts or PDC DMA, and free the controller when done. Device state includes MMIO register contents, clock enablement managed by implementations, and the `user` count in `struct ssc_device`.

## Dependencies And Integration Points
Depends on platform devices, lists, I/O helpers, clocks, DMA addresses, and Atmel platform data. Integrated by audio/I2S/PCM drivers, SPI-like synchronous serial users, PDC DMA, and Atmel SoC platform code.

## Risks And Test Signals
Raw MMIO macros do not enforce ordering or field range beyond masks. Wrong `has_fslen_ext` handling can program frame lengths incorrectly on older SoCs. Tests should cover request/free exclusivity, register field construction, RX/TX enable/disable, interrupt bits, PDC transfer setup, clock selection, DMA vs non-DMA operation, and audio DAI probe/use.
