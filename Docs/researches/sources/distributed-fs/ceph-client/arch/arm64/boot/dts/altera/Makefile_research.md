## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/altera/Makefile

### Purpose
Declares Intel/Altera SoCFPGA Stratix10 ARM64 DTB targets.

### Important APIs, Types, And Functions
Adds `socfpga_stratix10_socdk.dtb`, `socfpga_stratix10_socdk_emmc.dtb`, `socfpga_stratix10_socdk_nand.dtb`, and `socfpga_stratix10_swvp.dtb` under `CONFIG_ARCH_INTEL_SOCFPGA`.

### Control Flow
Kbuild builds these DTBs when Intel SoCFPGA support is configured.

### State, Persistence, And Dependencies
Build metadata only; depends on Stratix10 DTS files and common SoCFPGA includes.

### Integration Points
Adds Stratix10 board device trees to ARM64 DTB builds.

### Risks
Multiline target continuation must remain syntactically correct; stale board DTS names break all listed variants.

### Test Signals
Build Intel SoCFPGA DTBs and validate eMMC/NAND variant DTs with `dtc`.
