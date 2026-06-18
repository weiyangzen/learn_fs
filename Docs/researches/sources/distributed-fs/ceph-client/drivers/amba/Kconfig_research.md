# sources/distributed-fs/ceph-client/drivers/amba/Kconfig

### Purpose
This Kconfig file defines the AMBA bus enable symbol and the optional Tegra AHB configuration driver.

### Important APIs, Types, And Functions
There are no runtime APIs. `ARM_AMBA` is a boolean umbrella symbol. `TEGRA_AHB` is a boolean option visible under `COMPILE_TEST`, defaulting to yes on `ARCH_TEGRA`, with help text describing AHB arbitration and performance tuning.

### Control Flow
Configuration flow gates the Tegra AHB option inside `if ARM_AMBA`. Build inclusion then follows the Makefile's `obj-$(CONFIG_...)` rules.

### State, Persistence, And Dependencies
No runtime state exists. The file persists platform support decisions in kernel configuration. `TEGRA_AHB` depends implicitly on `ARM_AMBA` through menu nesting.

### Integration Points
It controls whether `bus.c` and `tegra-ahb.c` are buildable and exposes Tegra AHB support for Tegra platforms or compile-test builds.

### Risks
Misconfiguration can omit the AMBA bus or Tegra AHB performance setup. Because `TEGRA_AHB` defaults on for Tegra, changing defaults affects platform boot/performance assumptions.

### Test Signals
Kconfig tests should cover `ARCH_TEGRA`, `COMPILE_TEST`, and non-AMBA builds, confirming expected symbols and object inclusion.
