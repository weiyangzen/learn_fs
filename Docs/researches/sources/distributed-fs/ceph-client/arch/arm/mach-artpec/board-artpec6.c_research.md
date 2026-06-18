# sources/distributed-fs/ceph-client/arch/arm/mach-artpec/board-artpec6.c

Purpose: ARTPEC-6 board/machine support. It configures a syscon DMA request mode for PL011 UARTs and supplies a secure L2C310 register write callback using SMCCC SMC calls.

Control flow: `artpec6_init_machine` looks up `axis,artpec6-syscon` and writes `ARTPEC6_DMACFG_UARTS_BURST` to the DMA config register. `artpec6_l2c310_write_sec` calls secure monitor operation `SECURE_OP_L2C_WRITEREG` and warns on failure. The machine descriptor sets L2C aux value/mask, secure write callback, init hook, and DT match `axis,artpec6`. State is only external syscon/L2C hardware. Dependencies include syscon/regmap, SMCCC, L2C platform hooks, and DT root compatible. Risks are secure firmware call failure, syscon absence, and UART DMA mode mismatch. Test signals include boot without WARN_ON, UART DMA operation, and L2 cache initialization.
