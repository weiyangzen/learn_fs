# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/Kconfig

## Purpose
This file defines the AMD XDNA accelerator driver option for AMD AI Engine NPUs integrated into client CPUs.

## Important APIs, Types, And Functions
The key symbol is `CONFIG_DRM_ACCEL_AMDXDNA`, a tristate named "AMD AI Engine". It depends on `AMD_IOMMU`, `DRM_ACCEL`, `PCI`, `HAS_IOMEM`, and `X86_64`, and selects `DRM_SCHED`, `DRM_GEM_SHMEM_HELPER`, `FW_LOADER`, and `HMM_MIRROR`.

## Control Flow
When dependencies are met, the user can build the driver built-in or as module `amdxdna`. Selected helper symbols ensure scheduler, GEM shared-memory, firmware loading, and HMM mirror support are available.

## State, Dependencies, Integration, Risks, And Tests
State is Kconfig selection. Runtime integration depends on PCI discovery, AMD IOMMU/PASID/IOMMU paths, firmware loading, DRM scheduler, and HMM invalidation support. Risks include under-specified dependencies causing compile failures on unsupported architectures and over-strict dependencies hiding valid hardware. Test signals include Kconfig dependency matrix builds and verifying module build/load on supported AMD Ryzen AI platforms.
