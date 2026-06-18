# sources/distributed-fs/ceph-client/drivers/clk/socfpga/Makefile

Purpose: kbuild object mapping for Intel SoCFPGA clock drivers.

Important APIs/types/functions: `CLK_INTEL_SOCFPGA32` builds legacy/Arria10 helpers; `CLK_INTEL_SOCFPGA64` builds Stratix10 common helpers plus Agilex/Agilex5 drivers.

Control flow: enabled Kconfig symbols determine which object groups compile into the kernel.

State and persistence behavior: no runtime state.

Dependencies/integration points: object groups share `clk.h` and `stratix10-clk.h`.

Risks: new SoC support must be added to the correct family group; missing objects produce unresolved helper references.

Test signals: compile 32-bit-only, 64-bit-only, and combined configurations.
