# sources/distributed-fs/ceph-client/drivers/clk/uniphier/Makefile

Purpose: object list for UniPhier clock support.

Important APIs/types/functions: includes `clk-uniphier-core.o`, primitive helpers (`cpugear`, fixed-factor, fixed-rate, gate, mux), and SoC data objects (`sys`, `mio`, `peri`) in `obj-y`.

Control flow: build-time only. Once `CONFIG_CLK_UNIPHIER` causes this directory to build, all local objects are built in and the core builtin platform driver can reference data arrays and helper registration functions.

State and persistence: no runtime state, but the object ordering ensures core and helper/data code are linked together.

Dependencies/integration: integrates with the parent drivers/clk build. The use of `obj-y` aligns with builtin platform driver declarations.

Risks: adding a new UniPhier data/helper file requires updating this Makefile; otherwise compatible entries or helper symbols will be missing at link time.

Test signals: compile/link with `CONFIG_CLK_UNIPHIER=y`, verify all helper symbols resolve, and add build coverage when new UniPhier clock data files are introduced.
