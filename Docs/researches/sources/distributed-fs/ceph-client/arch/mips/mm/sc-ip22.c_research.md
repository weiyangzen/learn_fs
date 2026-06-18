<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-ip22.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/sc-ip22.c

### Purpose
`sc-ip22.c` implements Indy IP22 R4600/R5000 secondary-cache management. It probes cache size from SGI EEPROM, enables or disables the cache with CP0 mode switches, and provides DMA cache maintenance callbacks.

### Important APIs, Types, And Functions
`indy_sc_wipe()` performs the low-level indexed write sequence in inline MIPS3 assembly. `indy_sc_wback_invalidate()` handles range flushing with wraparound across the fixed 512 KiB index space. `indy_sc_enable()`, `indy_sc_disable()`, and `indy_sc_probe()` manage hardware state. `indy_sc_init()` installs `indy_sc_ops` into global `bcops`.

### Control Flow
Initialization reads EEPROM byte 17, computes cache size, enables the cache, and registers bcache operations. DMA cache maintenance computes first and last cache-line indexes, disables interrupts, and either wipes a contiguous range or splits the operation around the end of the index space.

### State, Persistence, And Dependencies
`scache_size` records probed size. Hardware state persists in secondary-cache enable bits and cache contents. Dependencies include SGI IP22 EEPROM access, CP0 status manipulation, KSEG address construction, and bcache operation dispatch.

### Integration Points
The file integrates with SGI IP22 platform setup and the generic MIPS bcache hooks used by DMA mapping and cache flush code.

### Risks
Inline assembly temporarily enters 64-bit mode from a 32-bit kernel context, so CP0 status save/restore and hazard nops are critical. The wipe algorithm assumes 32-byte lines and a 512 KiB index mask. `BUG_ON(size == 0)` catches bad DMA callers but turns misuse into a hard failure.

### Test Signals
Boot on IP22 with and without secondary cache, run DMA-heavy devices, validate wraparound range flushes, and verify CP0 status is restored after enable/disable and wipe operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-ip22.c -->
