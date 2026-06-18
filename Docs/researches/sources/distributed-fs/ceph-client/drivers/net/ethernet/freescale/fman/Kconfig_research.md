# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/Kconfig

### Purpose
`fman/Kconfig` defines build-time configuration for Freescale/NXP DPAA Frame Manager support and one DPAA FMan erratum workaround. It controls whether the FMan core, ports, and MAC support can be built.

### Important APIs, Types, And Functions
The user-visible symbol is `FSL_FMAN`, a tristate "FMan support" option depending on `FSL_SOC || ARCH_LAYERSCAPE || COMPILE_TEST`. It selects `GENERIC_ALLOCATOR`, `PHYLINK`, `PCS_LYNX`, and `CRC32`. The hidden bool `DPAA_ERRATUM_A050385` depends on `ARM64 && FSL_DPAA` and defaults to yes.

### Control Flow
There is no runtime control flow. Kconfig selection flow makes FMan objects eligible for compilation when SoC/platform or compile-test prerequisites are met, and automatically pulls required allocator, PHY link, Lynx PCS, and CRC dependencies. The erratum symbol enables software workaround code elsewhere for an FMan DMA transaction splitting issue.

### State, Persistence, And Dependencies
The file stores configuration state in the kernel `.config`. `FSL_FMAN` affects object inclusion via the sibling Makefile. `DPAA_ERRATUM_A050385` persists as a config symbol consumed by DPAA/FMan code paths.

### Integration Points
This Kconfig file integrates the `drivers/net/ethernet/freescale/fman` directory with the broader Freescale DPAA stack. `FSL_FMAN` is required by the Makefile objects `fsl_dpaa_fman.o`, `fsl_dpaa_fman_port.o`, and `fsl_dpaa_mac.o`, and by higher-level DPAA Ethernet components that depend on Frame Manager services.

### Risks
Missing selected dependencies would break link or runtime PHY integration. The erratum help text documents strict alignment constraints; disabling or misapplying the workaround under heavy traffic can stall packet processing through an internal FMan resource leak. Because `COMPILE_TEST` is allowed, code must build without real platform hardware.

### Test Signals
Configuration tests should cover `FSL_FMAN=m`, `FSL_FMAN=y`, and `COMPILE_TEST` builds. ARM64 DPAA builds should verify `DPAA_ERRATUM_A050385=y` and exercise traffic patterns with 4K-crossing DMA, unaligned DMA, and scatter-gather fragments not multiple of 16 bytes.
