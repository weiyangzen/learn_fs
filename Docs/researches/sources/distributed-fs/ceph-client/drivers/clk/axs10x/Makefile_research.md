<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/axs10x/Makefile

Purpose: This Makefile always builds the AXS10x I2S PLL and generic PLL clock drivers for this directory when the parent directory is included by Kbuild.

Important APIs, types, and functions: The functional lines are `obj-y += i2s_pll_clock.o` and `obj-y += pll_clock.o`. There are no runtime APIs.

Control flow: Kbuild includes both objects unconditionally within the AXS10x clock directory. The C files themselves decide their DT compatibility and platform-driver behavior.

State and persistence behavior: The file has no runtime state. Its persistent effect is to include both clock providers in the kernel image for the relevant build.

Dependencies and integration points: It integrates with the broader clock-driver Makefile that descends into `drivers/clk/axs10x`. The resulting drivers bind to Synopsys AXS10x PLL clock nodes.

Risks and test signals: The risk is build coverage rather than runtime logic. Test signals include successful allmodconfig/AXS10x builds and presence of both driver objects so ARC, PGU, and I2S PLL DT nodes can bind or initialize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/Makefile -->
