# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/Kconfig

Purpose: Defines kernel configuration options for IP-over-InfiniBand support, connected mode, and debug instrumentation.

Important APIs/types/functions: `CONFIG_INFINIBAND_IPOIB` is a tristate depending on `NETDEVICES && INET` and enables the IPoIB driver. `CONFIG_INFINIBAND_IPOIB_CM` is a bool depending on IPoIB that compiles connected-mode support. `CONFIG_INFINIBAND_IPOIB_DEBUG` defaults to yes and includes debug code/debugfs support when IPoIB is enabled. `CONFIG_INFINIBAND_IPOIB_DEBUG_DATA` depends on debug and adds data-path debug instrumentation.

Control flow: Kconfig presents these options during configuration and writes selected symbols into `.config`. The IPoIB Makefile then includes optional objects based on these symbols. Connected mode is compiled only when selected and still requires runtime mode changes through sysfs.

State and persistence behavior: Configuration choices persist in the kernel `.config` and determine compile-time object inclusion. There is no runtime state in this file, but help text documents sysfs and MTU implications.

Dependencies/integration: Integrates with kbuild and `ulp/ipoib/Makefile`. Runtime documentation is referenced through `Documentation/infiniband/ipoib.rst`. Connected mode affects `ipoib_cm.o`; debug affects `ipoib_fs.o` and module parameters/debugfs.

Risks: Debug defaults can increase compiled code and data-path debug can affect performance even when output is off. Connected mode help warns that multicast and UD traffic may drop unless destination MTU is constrained. Dependency changes can alter whether IPoIB is available on minimal networking builds.

Test signals: Kconfig dependency tests, build with IPoIB as built-in/module/off, connected mode on/off object inclusion, debugfs availability under debug, data-path performance comparison with debug data, and runtime MTU/mode sysfs behavior.
