# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5422-asv.h

## Purpose

`exynos5422-asv.h` is the small private header for Exynos5422 ASV support. It defines ASV subsystem ids and provides the build-time declaration or stub for `exynos5422_asv_init()`.

## Important APIs, Types, and Functions

The anonymous enum assigns `EXYNOS_ASV_SUBSYS_ID_ARM`, `EXYNOS_ASV_SUBSYS_ID_KFC`, and `EXYNOS_ASV_SUBSYS_ID_MAX`. The header forward-declares `struct exynos_asv`. With `CONFIG_EXYNOS_ASV_ARM`, it declares `int exynos5422_asv_init(struct exynos_asv *asv)`. Without that config, it supplies an inline stub returning `-ENOTSUPP`.

## Control Flow

Callers can invoke `exynos5422_asv_init()` unconditionally and receive either the real SoC implementation or a clear unsupported error depending on kernel configuration. The subsystem ids index the `asv->subsys[]` array populated by the C file.

## State and Persistence Behavior

This header owns no runtime state. Its enum values are ABI-like within the Exynos ASV implementation because they determine array indexing for ARM/KFC subsystem state.

## Dependencies and Integration Points

It depends on `linux/errno.h` for `-ENOTSUPP` and integrates the Exynos5422 implementation with the generic Exynos ASV code while avoiding link errors when ASV ARM support is disabled.

## Risks and Edge Cases

The enum order must stay synchronized with `exynos5422-asv.c`. Adding another subsystem requires updating `EXYNOS_ASV_SUBSYS_ID_MAX`, table setup, and callers. The stub makes unsupported builds fail at runtime rather than compile time, so callers must propagate nonzero return codes.

## Test Signals

Compile both `CONFIG_EXYNOS_ASV_ARM=y` and disabled variants. Runtime tests should verify unsupported configurations do not attempt to use uninitialized ASV subsystem data.
