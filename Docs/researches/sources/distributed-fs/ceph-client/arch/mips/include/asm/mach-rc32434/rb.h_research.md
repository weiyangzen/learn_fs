# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/rb.h

Purpose: RouterBOARD/IDT RC32434 board definitions for memory-mapped registers, GPIO latch bits, external device windows, and board-local device bookkeeping. The header is a low-level platform contract for RC32434 board code and drivers, not a standalone implementation.

Important APIs/types/functions: `REGBASE`, `IDT434_REG_BASE`, `UART0BASE`, `DEV{0..3}{BASE,MASK,C,TC}`, `BTCS`, and `BTCOMPARE` describe register offsets. `LO_WPX`, `LO_ALE`, `LO_CLE`, `LO_CEX`, `LO_FOFF`, `LO_SPICS`, and `LO_ULED` name latch lines. `struct dev_reg` models a base/mask/control/timing register bank. `struct korina_device` carries an Ethernet name, MAC address, and `net_device`. `struct mpmc_device` stores latch/controller state, a spinlock, and an I/O base. `set_latch_u5()` and `get_latch_u5()` are external latch accessors.

Control flow, state, and persistence: The header exposes shared MMIO layout and volatile latch state; control flow lives in platform code that maps `KSEG1ADDR(REGBASE)` and calls the latch helpers. State persists only in device registers and `mpmc_device.state`, guarded by `mpmc_device.lock`.

Dependencies and integration: It depends on MIPS `KSEG1ADDR`, Linux `u32`, `spinlock_t`, `__iomem`, and networking types supplied by including code. It integrates with NAND/SPI/LED control, Korina Ethernet, and RC32434 platform setup.

Risks and test signals: Hard-coded physical offsets make this sensitive to SoC variants. Test by compiling the RC32434 platform, validating latch bit transitions on hardware, and checking Ethernet/NAND boot paths that consume `korina_device` and device window registers.
