# sources/distributed-fs/ceph-client/drivers/clk/socfpga/Kconfig

Purpose: configuration for Intel SoCFPGA/eASIC clock-controller support.

Important APIs/types/functions: `CLK_INTEL_SOCFPGA`, `CLK_INTEL_SOCFPGA32`, and `CLK_INTEL_SOCFPGA64`.

Control flow: selected symbols drive the SoCFPGA Makefile object sets for 32-bit legacy and 64-bit Stratix/Agilex families.

State and persistence behavior: no runtime state.

Dependencies/integration points: defaults to `ARCH_INTEL_SOCFPGA` with architecture-specific and `COMPILE_TEST` dependencies.

Risks: wrong architecture gating can omit required clock objects or hide compile-test coverage.

Test signals: ARM, ARM64, ARCH_INTEL_SOCFPGA, and COMPILE_TEST build matrix.
