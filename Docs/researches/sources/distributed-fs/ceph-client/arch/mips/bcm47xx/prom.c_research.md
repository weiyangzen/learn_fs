# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/prom.c

Purpose: BCM47xx early PROM and memory setup. It identifies the system type, imports bootloader command-line data, adds RAM regions, and handles high-memory TLB preparation for some BMIPS configurations.

Important APIs and functions: `get_system_type()` returns the selected system string. `bcm47xx_set_system_type()` formats chip IDs into a Broadcom system name. `prom_init_mem()` adds the low memory region, including a fallback for CFE-less boot. `prom_init()` handles CFE presence, boot argument parsing, board detection, and memory setup. `early_tlb_init()` and `bcm47xx_prom_highmem_init()` install fixed TLB mappings for high memory when compiled for BMIPS highmem support.

Control flow: MIPS early boot calls `prom_init`; it records firmware parameters, initializes CFE access when available, discovers the board, appends boot arguments, and calls memory setup. Highmem setup runs later but still during early architecture initialization.

State and persistence: mutates global boot state such as `arcs_cmdline`, board metadata, memblock memory regions, and fixed TLB entries. Nothing persists after reboot.

Dependencies and integration points: relies on CFE conventions, SSB chipcommon UART address constants, MIPS memblock/TLB APIs, BMIPS helpers, and `bcm47xx_board_detect()`. It feeds later platform setup, CPU info, and the physical memory allocator.

Risks and test signals: early-boot failures are severe: wrong memory bounds or TLB mappings can crash before console is stable. Test signals include early console output, `/proc/cmdline`, `/proc/iomem`, detected system type, highmem visibility, and successful boot on both CFE and non-CFE BCM47xx devices.
