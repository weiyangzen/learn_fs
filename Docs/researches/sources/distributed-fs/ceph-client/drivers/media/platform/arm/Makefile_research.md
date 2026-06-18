# sources/distributed-fs/ceph-client/drivers/media/platform/arm/Makefile

Purpose: Adds the ARM Mali-C55 media platform subdirectory to the kernel build.

Important APIs/types/functions: No C symbols; `obj-y += mali-c55/` ensures the subdirectory Makefile participates in built-in and module resolution.

Control flow and state: Kbuild descends into `mali-c55/` unconditionally, while object selection inside that directory depends on `CONFIG_VIDEO_MALI_C55`.

Dependencies and integration: Paired with `arm/Kconfig` and `arm/mali-c55/Makefile`.

Risks: Unconditional descent is normal for Kbuild, but missing subdirectory files or stale object names fail build-time.

Test signals: Compile with `CONFIG_VIDEO_MALI_C55=m`, `=y`, and unset.
