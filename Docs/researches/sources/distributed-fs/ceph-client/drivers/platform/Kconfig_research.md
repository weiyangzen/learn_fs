# sources/distributed-fs/ceph-client/drivers/platform/Kconfig

Purpose: top-level Kconfig aggregator for platform-specific drivers under `drivers/platform`. It does not define options itself; it sources architecture/vendor submenus.

Important APIs, types, and functions: sources `mips`, `loongarch`, `goldfish`, `chrome`, `cznic`, `mellanox`, `olpc`, `surface`, `x86`, `arm64`, `raspberrypi`, and `wmi` Kconfig files.

Control flow: during Kconfig parsing, this file makes each subordinate platform menu visible according to its own dependencies. Option symbols from those files are later consumed by `drivers/platform/Makefile`.

State and persistence: no runtime state. Build configuration persists in generated kernel `.config`.

Dependencies and integration points: integrated by the kernel's drivers Kconfig hierarchy. Ordering can affect menu display but not object linking directly.

Risks and edge cases: missing a `source` line hides an entire platform family. Adding a submenu here without a matching Makefile dispatch can make options selectable but unbuilt.

Test signals: `make menuconfig`/`olddefconfig` parse success and all sourced paths existing in tree. Build tests should toggle representative symbols and verify Makefile traversal.
