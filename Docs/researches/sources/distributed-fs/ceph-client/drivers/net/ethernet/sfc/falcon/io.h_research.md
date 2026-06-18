# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/io.h

## Purpose
`io.h` provides inline MMIO and SRAM accessors for Falcon-architecture NICs. It centralizes the Bus Interface Unit locking rules for 128-bit CSRs and 64-bit SRAM, while allowing special fast-path dword writes for descriptor doorbells and event/timer page registers.

## Important APIs, Types, And Functions
Raw helpers `_ef4_writeq()`, `_ef4_readq()`, `_ef4_writed()`, and `_ef4_readd()` wrap unformatted MMIO reads/writes against `efx->membase`. Public accessors include `ef4_writeo()`/`ef4_reado()` for 128-bit CSRs, `ef4_writed()`/`ef4_readd()` for 32-bit CSRs, `ef4_sram_writeq()`/`ef4_sram_readq()` for mapped 64-bit SRAM, and table helpers `ef4_writeo_table()`/`ef4_reado_table()`. Page-mapped helpers use `EF4_VI_PAGE_SIZE` and `EF4_PAGED_REG()` for per-VI registers, including `_ef4_writeo_page()`, `_ef4_writed_page()`, and `_ef4_writed_page_locked()`.

## Control Flow
Wide CSR/SRAM reads and writes take `efx->biu_lock`, perform ordered dword or qword operations depending on `BITS_PER_LONG`, then release the lock. Dword writes intentionally avoid the lock because 32-bit registers and special descriptor-update high-dword writes are safe without it. The page-write macros include compile-time register filters using `BUILD_BUG_ON_ZERO` so only known safe page-mapped registers are accepted. `TIMER_COMMAND` page zero is locked because of a BIU collector bug.

## State And Persistence
The accessors mutate or read hardware state in PCI BAR space and mapped SRAM. They also serialize access through `efx->biu_lock`, preventing interleaved wide writes from corrupting the BIU collector. No software state is persisted except debug logging and the lock's synchronization effect.

## Dependencies And Integration Points
This file depends on Linux MMIO primitives, spinlocks, `netif_vdbg`, and the driver's bitfield word types from surrounding headers. It is the foundation for register dump code, queue setup, buffer table programming, interrupt/event operations, filter programming, MAC/PHY management registers, and statistic DMA controls.

## Risks
The largest risk is violating the BIU collector semantics by using an unlocked wide access or the wrong accessor width. The special descriptor-update path is intentionally narrow: writing the wrong dword can be discarded or write zero to unintended bits. Page helpers hard-code register-address allowances; adding a new page-mapped register requires revisiting these compile-time guards. Endianness and raw access also matter because the helper casts between little-endian driver word types and CPU raw IO values.

## Test Signals
Relevant tests include register self-tests, queue doorbell traffic, RX/TX descriptor updates, event queue read-pointer updates, timer moderation behavior, register dumps under load, and stress tests with concurrent queues. Hardware symptoms of access bugs include lost writes, stuck queues, missing interrupts, queue flush timeouts, and inconsistent register dump values.
