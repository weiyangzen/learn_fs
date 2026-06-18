<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/meson8-ddr-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/meson8-ddr-clkc.h

Purpose: Provides the minimal DT clock IDs for the Amlogic Meson8 DDR clock controller.

Important APIs, types, and functions: Defines `DDR_CLKID_DDR_PLL_DCO` and `DDR_CLKID_DDR_PLL`. No functions, structs, or macros with behavior are present.

Control flow: No control flow exists. Consumers and the DDR clock provider use the two IDs to identify the PLL DCO and PLL output.

State and persistence: These constants are the stable DT ABI for the DDR clock provider. Hardware state, rate programming, and parent selection are implemented in the Meson clock driver.

Dependencies and integration points: Included by Meson8 DT sources or bindings that reference DDR PLL clock specifiers. Integrates with the common clock framework and Amlogic Meson clock drivers.

Risks and test signals: Risks are small but ABI-sensitive: changing either value would silently point DT consumers at the wrong DDR clock. Test with DT compilation, Meson8 clock provider probe, DDR PLL rate reporting, memory stability tests, and absence of `of_clk_get()` failures for DDR-related nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/meson8-ddr-clkc.h -->
