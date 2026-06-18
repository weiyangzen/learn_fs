# sources/distributed-fs/ceph-client/drivers/clk/mxs/Makefile

Purpose: Builds the Freescale/NXP MXS clock support. The common helper objects are always linked for this directory, while SoC-specific clock-topology files are conditional on i.MX23 and i.MX28 configuration.

Important APIs, types, and functions: The make targets include `clk.o`, `clk-pll.o`, `clk-ref.o`, `clk-div.o`, `clk-frac.o`, and `clk-ssp.o` unconditionally. `clk-imx23.o` is selected by `CONFIG_SOC_IMX23`; `clk-imx28.o` is selected by `CONFIG_SOC_IMX28`.

Control flow: Kbuild composes the MXS clock directory into the kernel. The object split matches the code design: reusable CCF primitives and SSP helper support are separated from SoC-specific OF early clock declarations.

State and persistence: No runtime state. The file controls which object files are present in the final kernel image.

Dependencies and integration points: Depends on parent Kbuild entering this directory only when MXS clock support is required. The conditional SoC objects must match the symbols that provide their `CLK_OF_DECLARE()` hooks and exported SoC helper APIs.

Risks: Because helpers are `obj-y`, they are built whenever the directory is included; stale helper dependencies would affect both i.MX23 and i.MX28. Missing SoC config prevents the matching one-cell provider from being present even if the DT node exists.

Test signals: Build coverage should include `CONFIG_SOC_IMX23`, `CONFIG_SOC_IMX28`, and both enabled. Link errors around `mxs_clk_*` helpers or missing `mxs_saif_clkmux_select()` would indicate Makefile coverage issues.
