# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/Kconfig

## Purpose
This Kconfig entry exposes the Panfrost DRM driver for ARM Mali Midgard and Bifrost GPUs.

## Important APIs, Types, and Functions
It defines `config DRM_PANFROST` as a tristate. It selects DRM scheduler, IOMMU LPAE page-table support, GEM shmem helpers, PM devfreq with simple_ondemand governor, and device coredump support.

## Control Flow
There is no runtime control flow. Build selection is gated on DRM, ARM/ARM64 or compile-test, absence of `GENERIC_ATOMIC64`, and MMU support.

## State and Persistence Behavior
The file stores build-time dependency state only. Enabling it causes the Panfrost module or built-in object to compile and makes dependent subsystems available.

## Dependencies and Integration Points
The entry integrates Panfrost with the DRM core, IOMMU io-pgtable LPAE backend, DRM GPU scheduler, shmem GEM helpers, devfreq, thermal/devfreq governor infrastructure, and devcoredump.

## Risks
The `!GENERIC_ATOMIC64` dependency is tied to LPAE page-table implementation constraints and can surprise compile-test coverage. Missing selected subsystems would break core driver features such as MMU mapping, scheduling, GEM allocation, and crash dumps.

## Test Signals
Build tests should cover built-in and module configurations on ARM, ARM64, and COMPILE_TEST platforms, including dependency resolution for `DRM_SCHED`, `IOMMU_IO_PGTABLE_LPAE`, `PM_DEVFREQ`, and `WANT_DEV_COREDUMP`.
