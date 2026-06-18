# sources/distributed-fs/ceph-client/drivers/clk/keystone/Kconfig Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/clk/keystone/Kconfig

### Purpose
This Kconfig file exposes TI Keystone/K3 clock drivers: legacy Keystone PLL/PSC clocks, TI System Control Interface clocks, optional firmware scanning, and syscon-backed gate clocks.

### Important APIs, Types, And Functions
Symbols are `COMMON_CLK_KEYSTONE`, `TI_SCI_CLK`, `TI_SCI_CLK_PROBE_FROM_FW`, and `TI_SYSCON_CLK`. `TI_SCI_CLK` depends on `TI_SCI_PROTOCOL`; `TI_SYSCON_CLK` defaults on Keystone or K3; legacy common Keystone clocks depend on OF and Keystone architecture or compile testing.

### Control Flow, State, And Persistence
The file controls which objects in `drivers/clk/keystone/Makefile` are built. `TI_SCI_CLK_PROBE_FROM_FW` changes sci-clk discovery behavior at compile time: firmware-wide probing instead of DT-demand discovery. There is no runtime state here, but build selections determine which OF compatibles and platform drivers are available.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include architecture symbols, OF, the TI SCI protocol driver, and COMPILE_TEST. Risks include enabling SCI clocks without protocol support, firmware probing increasing boot time, and default symbol choices not matching board DTs. Test signals are Keystone and K3 defconfigs, allmodconfig, boot with TI SCI firmware, and DT nodes matching selected drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/Kconfig -->
