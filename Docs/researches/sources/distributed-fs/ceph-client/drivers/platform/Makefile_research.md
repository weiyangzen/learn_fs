# sources/distributed-fs/ceph-client/drivers/platform/Makefile

Purpose: top-level build dispatch for `drivers/platform`, mapping configuration symbols to architecture/vendor subdirectories.

Important APIs, types, and functions: `obj-$(CONFIG_...) += dir/` entries select `x86`, `loongarch`, `mellanox`, `mips`, `olpc`, `goldfish`, `chrome`, `cznic`, `surface`, `arm64`, `raspberrypi`, and `wmi` subdirectories.

Control flow: kbuild descends into a subdirectory when the associated symbol is enabled. Some entries are architecture gates (`CONFIG_X86`, `CONFIG_MIPS`), while others are menuconfig/vendor symbols (`CONFIG_CHROME_PLATFORMS`, `CONFIG_ARM64_PLATFORM_DEVICES`).

State and persistence: no runtime state. It affects built-in and module object graph only.

Dependencies and integration points: must stay aligned with `drivers/platform/Kconfig` and subdirectory Makefiles. Subdirectory Makefiles perform per-driver object selection.

Risks and edge cases: using a broad architecture symbol can build a directory whenever the architecture is selected, relying on the child Makefile to avoid unwanted objects. A Kconfig symbol without a Makefile entry results in dead configuration.

Test signals: kbuild traversal with multiple architecture/config combinations, especially `COMPILE_TEST`, and `make W=1` for stale object names.
