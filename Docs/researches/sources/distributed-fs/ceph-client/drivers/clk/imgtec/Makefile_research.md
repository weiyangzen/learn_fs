## sources/distributed-fs/ceph-client/drivers/clk/imgtec/Makefile

### Purpose
`imgtec/Makefile` maps the Boston clock Kconfig symbol to its object file.

### Important APIs, Types, And Functions
It contains `obj-$(CONFIG_COMMON_CLK_BOSTON) += clk-boston.o`.

### Control Flow
The kernel build system includes `clk-boston.o` only when `COMMON_CLK_BOSTON` is enabled.

### State, Persistence, And Dependencies
No runtime state. It depends on the Kconfig symbol from the same directory.

### Integration Points
Connects the Kconfig option to the actual clock driver.

### Risks
Minimal. A symbol rename without Makefile update would silently drop the driver from builds.

### Test Signals
Run `make drivers/clk/imgtec/` with `CONFIG_COMMON_CLK_BOSTON=y` and confirm `clk-boston.o` is compiled.
