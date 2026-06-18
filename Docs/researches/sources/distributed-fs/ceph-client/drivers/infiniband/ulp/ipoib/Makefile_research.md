# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/Makefile

Purpose: Defines the kbuild object composition for the IPoIB kernel module/object.

Important APIs/types/functions: `obj-$(CONFIG_INFINIBAND_IPOIB) += ib_ipoib.o` creates the aggregate IPoIB target. `ib_ipoib-y` always includes `ipoib_main.o`, `ipoib_ib.o`, `ipoib_multicast.o`, `ipoib_verbs.o`, `ipoib_vlan.o`, `ipoib_ethtool.o`, and `ipoib_netlink.o`. `ib_ipoib-$(CONFIG_INFINIBAND_IPOIB_CM)` conditionally adds `ipoib_cm.o`. `ib_ipoib-$(CONFIG_INFINIBAND_IPOIB_DEBUG)` conditionally adds `ipoib_fs.o`.

Control flow: Kbuild builds the aggregate object from the listed components when IPoIB is enabled. Optional connected-mode and debug source files are compiled into the same aggregate only when their config symbols are true. There is no runtime logic here.

State and persistence behavior: No runtime state. Build output is determined by persistent kernel configuration.

Dependencies/integration: Driven by `ulp/ipoib/Kconfig` and included by `ulp/Makefile`. The object grouping means symbol visibility and initialization are linked into one driver target, with optional feature code compiled in or absent.

Risks: Forgetting to add a new source file here will produce unresolved symbols or missing functionality. Optional object guards must match the C preprocessor expectations in IPoIB sources. Debug object inclusion changes debugfs/module-parameter behavior.

Test signals: Build all config combinations: base IPoIB only, connected mode, debug, debug-data, and module/built-in. Inspect `ib_ipoib.o` composition or build logs, and run modpost to catch unresolved references from optional code.
