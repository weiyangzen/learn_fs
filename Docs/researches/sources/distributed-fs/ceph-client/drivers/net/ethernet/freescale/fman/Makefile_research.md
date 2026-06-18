# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/Makefile

### Purpose
`fman/Makefile` defines how the Freescale/NXP DPAA Frame Manager directory is compiled. It groups source files into three logical kernel objects: FMan core, FMan port, and FMan MAC support.

### Important APIs, Types, And Functions
The Makefile adds the FMan directory to `subdir-ccflags-y` include search paths, then builds `fsl_dpaa_fman.o`, `fsl_dpaa_fman_port.o`, and `fsl_dpaa_mac.o` when `CONFIG_FSL_FMAN` is enabled. Object composition is `fman_muram.o fman.o fman_sp.o fman_keygen.o` for the core, `fman_port.o` for ports, and `mac.o fman_dtsec.o fman_memac.o fman_tgec.o` for MAC support.

### Control Flow
Build flow is controlled by Kbuild. Enabling `CONFIG_FSL_FMAN` causes all three composite objects to be compiled and linked into the kernel or module according to the tristate setting. The include flag ensures local headers such as `fman.h`, `fman_port.h`, and MAC-specific headers are found consistently.

### State, Persistence, And Dependencies
No runtime state exists. Build state is captured by Kbuild variables and `CONFIG_FSL_FMAN`. The object lists depend on the FMan source files in the same directory and on Kconfig-selected dependencies such as PHYLINK, PCS_LYNX, GENERIC_ALLOCATOR, and CRC32.

### Integration Points
This file is the build integration point between FMan source modules and the kernel networking tree. The composite objects separate reusable FMan core services, port management, and MAC implementations for dTSEC, mEMAC, and TGEC.

### Risks
Object grouping is part of symbol availability. Removing a source from the wrong composite object could produce unresolved symbols or feature loss in DPAA Ethernet drivers. The broad local include path can hide missing explicit include relationships, so header refactors should be build-tested carefully.

### Test Signals
Run build tests with `CONFIG_FSL_FMAN=y` and `m`, plus `COMPILE_TEST`. Confirm the three composite objects are produced, module dependencies resolve, and DPAA Ethernet users link against the expected FMan symbols.
