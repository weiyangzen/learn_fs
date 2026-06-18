# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_regs.h

Purpose: maps SB1250 on-chip peripheral register addresses and physical address windows. It is the base address/offset catalog used by platform code and low-level drivers for memory controller, L2 cache, PCI/LDT, MAC/DMA, DUART, synchronous serial, generic bus, GPIO, SMBus, timers, SCD, address traps, interrupt mapper, performance counters, bus watcher, debug/trace, data mover, and the physical map.

Important APIs/types/functions: the API consists of `A_*` absolute address macros, `R_*` register offsets, and parameterized helpers such as `A_MC_REGISTER`, `A_MAC_REGISTER`, `A_MAC_DMA_REGISTER`, `A_DUART_CHANREG`, `A_SER_REGISTER`, `A_IO_EXT_REG`, `A_SMB_REGISTER`, `A_SCD_TIMER_REGISTER`, `A_ADDR_TRAP_UP`, `A_IMR_REGISTER`, `A_MAILBOX_REGISTER`, `A_SCD_PERF_CNT`, and `A_DM_REGISTER`. Physical map constants include memory windows, system control, generic bus, LDT/PCI windows, cache test space, and cache way ranges.

Control flow: callers compose base-plus-offset addresses, then use MMIO helpers to initialize devices, route interrupts, access UARTs, drive timers, configure external buses, and control DMA. Feature gates remove blocks not present on 112x/1250 variants, such as memory controllers, sync serial, PCI/HT, and newer counters.

State and persistence: the file stores no state; all addresses target hardware state. Some macros target write-side set/clear aliases or debug/status views that must be used with the correct access semantics.

Dependencies and integration: depends on `sb1250_defs.h` and underpins nearly every other SiByte header. `bcm1480_regs.h` includes this file for shared blocks and adds BCM1480-specific addresses where layouts changed.

Risks and test signals: off-by-spacing errors or using feature-gated addresses on the wrong SoC can hang MMIO. The file includes compatibility aliases that comments discourage, so new code should prefer specific register names. Test signals include all-platform compile coverage, boot-time UART/timer/interrupt smoke tests, MAC/DMA and SMBus probing, generic-bus resource checks, and address-map validation against SoC documentation or hardware reads.
