# sources/distributed-fs/ceph-client/drivers/soc/canaan/Kconfig

Purpose: Kconfig entry for the Canaan Kendryte K210 system controller driver.

Important configuration: `SOC_K210_SYSCTL` is a boolean option depending on `RISCV`, `SOC_CANAAN_K210`, `OF`, and `COMMON_CLK_K210`; it defaults to `SOC_CANAAN_K210` and selects `PM` and `MFD_SYSCON`.

Control flow and integration: enabling this option builds the K210 system controller driver that performs early clock setup and populates sysctl child devices. The `COMMON_CLK_K210` dependency is essential because the C file calls `k210_clk_early_init()`.

State and persistence: no runtime state is defined in Kconfig; it gates build-time inclusion and selected framework dependencies.

Risks and test signals: risks are underselecting dependencies for early clock/syscon use or enabling the driver without OF. Test signals are Kconfig satisfiability for K210 RISC-V defconfigs and no missing symbol link errors.
