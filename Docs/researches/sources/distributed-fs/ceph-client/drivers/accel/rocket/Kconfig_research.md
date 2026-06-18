# sources/distributed-fs/ceph-client/drivers/accel/rocket/Kconfig

Purpose: defines the build-time configuration for the Rockchip NPU DRM accel driver.

Important APIs and types: declares `CONFIG_DRM_ACCEL_ROCKET` as a tristate option titled "Rocket (support for Rockchip NPUs)".

Control flow: selecting the option enables compilation of the `rocket` module. It depends on DRM accel support, ARM64 Rockchip or compile-test, Rockchip IOMMU or compile-test, and MMU; it selects DRM scheduler and GEM shmem helper support.

State and persistence: no runtime state. It controls whether the source files are built into the kernel or module.

Dependencies and integration: points users to `include/uapi/drm/rocket_accel.h` and the Mesa3D Rocket userspace driver. The hardware target is RK3588/RKNN/RKNPU-class NPUs.

Risks and test signals: build-test with native Rockchip configs and `COMPILE_TEST`, ensuring all selected helper dependencies are sufficient and module naming matches `rocket`.
