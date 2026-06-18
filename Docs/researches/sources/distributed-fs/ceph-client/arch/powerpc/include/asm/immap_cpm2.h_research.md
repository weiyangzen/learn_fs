# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/immap_cpm2.h

Purpose: Defines the CPM2 internal memory map for classic embedded PowerPC SoCs, including SIU, interrupt controller, timers, DMA, FCC/SCC/SMC, USB, and dual-port RAM regions.

Important APIs, types, and functions: Provides many packed register-map structs, `cpm2_map_t` for the full IMMR layout, PISCR bit definitions, `im_dprambase`, and global mapped pointer `cpm2_immr`.

Control flow: CPM2 platform and driver code maps the IMMR, casts it to `cpm2_map_t`, then accesses sub-block registers for communication controllers, timers, DMA, and interrupt/pin configuration.

State and persistence: State is hardware MMIO register content and dual-port RAM. `cpm2_immr` is a runtime mapping pointer.

Dependencies and integration points: Integrates CPM2 serial, Ethernet, USB, DMA, interrupt, and board setup drivers. It depends on exact SoC register layout and `__iomem` access discipline.

Risks: This is a large hardware ABI map; padding/reserved fields must remain exact. Direct struct MMIO access is fragile across endian, alignment, and compiler packing assumptions. Wrong offsets can affect unrelated peripherals.

Test signals: CPM2 board boot, serial/FCC/SCC/SMC operation, timer interrupts, DMA transfers, USB if present, dual-port RAM allocation, and compile-time offset checks against datasheets.
