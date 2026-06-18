<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-hr2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-hr2.c

Purpose: This wrapper registers Hurricane 2 ARM PLL support through the shared iProc ARM PLL helper.

Important APIs, types, and functions: `hr2_armpll_init()` calls `iproc_armpll_setup(node)`. It is registered by `CLK_OF_DECLARE(..., "brcm,hr2-armpll", ...)`.

Control flow: Early OF initialization matches the HR2 compatible and delegates all setup to the common iProc ARM PLL implementation.

State and persistence behavior: There is no local state. Hardware mapping, rate calculation state, and provider registration are handled in `clk-iproc-armpll.c`.

Dependencies and integration points: It depends on `clk-iproc.h`, the common iProc helper object, and the HR2 DT compatible. It provides the ARM PLL clock for Broadcom Hurricane 2 platforms.

Risks and test signals: Risks are limited to missing helper build coverage or compatible mismatch. Test signals include provider registration and correct ARM clock rate calculation on HR2 hardware or DT tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-hr2.c -->
