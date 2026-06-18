# sources/distributed-fs/ceph-client/include/soc/canaan/k210-sysctl.h

Purpose: provides Kendryte K210 system-controller register offsets and the early clock initialization hook.

Important APIs and types: macros enumerate register offsets for Git ID, UART baud, PLL controllers, PLL lock, ROM error, clock selection, central/peripheral clock enables, soft/peripheral resets, clock thresholds, miscellaneous/peripheral control, SPI sleep, reset status, DMA handshake selectors, and IO power mode. `k210_clk_early_init(void __iomem *regs)` is the public early clock setup entry.

Control flow: early platform code maps SYSCTL, calls `k210_clk_early_init()`, and later clock/reset drivers program PLLs, gates, resets, thresholds, DMA selectors, and power mode registers through these offsets.

State and persistence: SYSCTL MMIO state controls clocks, resets, and power behavior until reset or reprogramming. No software state is held in the header.

Dependencies and integration points: requires `__iomem` context from includers and integrates K210 clock, reset, serial, DMA, and power setup.

Risks and test signals: risks include early init before safe MMIO mapping, PLL lock sequencing, reset register misuse, and register offset drift from vendor SDK assumptions. Test early console clocking, PLL/gate changes, peripheral reset behavior, DMA handshake selection, and build coverage for RISC-V K210 configs.
