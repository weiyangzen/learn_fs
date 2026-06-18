# sources/distributed-fs/ceph-client/drivers/amba/Makefile

### Purpose
This Makefile maps AMBA-related configuration symbols to object files.

### Important APIs, Types, And Functions
There are no runtime APIs. `CONFIG_ARM_AMBA` builds `bus.o`; `CONFIG_TEGRA_AHB` builds `tegra-ahb.o`.

### Control Flow
Kbuild expands object lists according to configuration. `bus.o` provides the core AMBA bus type and exported helpers; `tegra-ahb.o` provides NVIDIA Tegra AHB register programming.

### State, Persistence, And Dependencies
No runtime state exists. The Makefile depends on Kconfig symbols from the same directory and architecture/platform selections.

### Integration Points
It connects AMBA core support and Tegra-specific AHB support into the kernel driver build.

### Risks
Wrong object mapping causes missing bus registration or missing Tegra AHB init. Since AMBA drivers depend on `amba_bustype`, omitting `bus.o` breaks all AMBA device binding.

### Test Signals
Build tests should verify object inclusion for `CONFIG_ARM_AMBA=y` and `CONFIG_TEGRA_AHB=y`, plus absence when disabled.
