# sources/distributed-fs/ceph-client/drivers/clk/keystone/Makefile Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/Makefile -->
## sources/distributed-fs/ceph-client/drivers/clk/keystone/Makefile

### Purpose
The Keystone Makefile connects Keystone/K3 clock Kconfig symbols to their implementation objects.

### Important APIs, Types, And Functions
It builds `pll.o gate.o` for `CONFIG_COMMON_CLK_KEYSTONE`, `sci-clk.o` for `CONFIG_TI_SCI_CLK`, and `syscon-clk.o` for `CONFIG_TI_SYSCON_CLK`.

### Control Flow, State, And Persistence
Build flow is direct object selection. The legacy PLL and PSC gate implementations are bundled under the common Keystone symbol, while TI SCI and syscon gate drivers are independently selectable and can be modular.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile must match Kconfig and module metadata in the C files. Risks are link failures from stale object selection or missing objects for a compatible used in DT. Test signals include modular and built-in builds for each symbol and boot-time probing of the selected OF/platform drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/Makefile -->
