# sources/distributed-fs/ceph-client/drivers/clk/Kconfig

Purpose: this is the top-level Kconfig switchboard for the Linux common clock framework and its clock-provider drivers. It defines the base API symbols `HAVE_CLK`, `HAVE_CLK_PREPARE`, `HAVE_LEGACY_CLK`, and `COMMON_CLK`, then exposes many provider-specific options and sources vendor subdirectories.

Important symbols and integration points: `COMMON_CLK` selects `HAVE_CLK`, `HAVE_CLK_PREPARE`, and `RATIONAL`, and is mutually exclusive with legacy architecture clock implementations. Driver symbols such as `COMMON_CLK_SCMI`, `COMMON_CLK_SCPI`, `COMMON_CLK_SI5341`, `COMMON_CLK_RK808`, `COMMON_CLK_RPMI`, and many others describe dependencies on buses, MFD parents, firmware protocols, OF, architecture families, or `COMPILE_TEST`. The file sources vendor Kconfig fragments including `actions`, `analogbits`, `aspeed`, `bcm`, `qcom`, `renesas`, `rockchip`, `ti`, and `xilinx`.

Control flow/state: Kconfig has no runtime state, but it gates which object files are compiled and which symbols become visible to dependent drivers. `default` clauses mostly follow architecture or parent-device selections. The final KUnit options select clock tests and device-tree overlays.

Dependencies and risks: incorrect dependencies can silently build unsupported drivers, hide required clocks, or break compile-test coverage. The top-level `source` list is an integration dependency for every vendor subtree. Test signals are `make olddefconfig`, per-architecture defconfigs, `COMPILE_TEST`, and the clock KUnit symbols.
