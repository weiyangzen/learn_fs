## sources/distributed-fs/ceph-client/drivers/clk/imgtec/Kconfig

### Purpose
`imgtec/Kconfig` declares the build option for the Imagination Technologies MIPS Boston board clock driver.

### Important APIs, Types, And Functions
The only symbol is `COMMON_CLK_BOSTON`, a bool depending on `MIPS || COMPILE_TEST` and selecting `MFD_SYSCON`.

### Control Flow
Kconfig selection controls whether `clk-boston.o` is built via the Makefile. Selecting syscon ensures the driver can access its parent platform register map.

### State, Persistence, And Dependencies
No runtime state. The dependency model restricts normal builds to MIPS while preserving compile-test coverage.

### Integration Points
The symbol feeds `drivers/clk/imgtec/Makefile` and supports the `img,boston-clock` DT clock provider.

### Risks
Because the option is bool and early-OF based, it cannot be runtime loaded as a module. Missing `MFD_SYSCON` selection would break register access, but the file handles that.

### Test Signals
Kconfig coverage includes MIPS defconfigs and `COMPILE_TEST=y`, confirming `COMMON_CLK_BOSTON` selects syscon and builds cleanly.
