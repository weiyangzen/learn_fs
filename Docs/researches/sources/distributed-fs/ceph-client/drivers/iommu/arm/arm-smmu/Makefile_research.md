<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/Makefile

## Purpose

This Makefile selects the objects that build the legacy Arm SMMU v1/v2 driver. It wires the common `arm_smmu` module/built-in object from the core driver, implementation-quirk file, and NVIDIA integration file, and conditionally includes Qualcomm support objects.

## Important APIs, Types, and Functions

There are no C APIs in this file. Its important build targets are `qcom_iommu.o`, `arm_smmu.o`, `arm-smmu.o`, `arm-smmu-impl.o`, `arm-smmu-nvidia.o`, `arm-smmu-qcom.o`, and `arm-smmu-qcom-debug.o`. The `arm_smmu-objs` assignment means the final `arm_smmu` object always includes the core, generic implementation quirks, and NVIDIA implementation code when `CONFIG_ARM_SMMU` is enabled.

## Control Flow

Kbuild evaluates the `obj-*` and `arm_smmu-*` variables based on configuration symbols. `CONFIG_QCOM_IOMMU` builds a separate Qualcomm IOMMU driver object. `CONFIG_ARM_SMMU` builds the Arm SMMU aggregate. `CONFIG_ARM_SMMU_QCOM` appends Qualcomm Arm SMMU implementation support to that aggregate. `CONFIG_ARM_SMMU_QCOM_DEBUG` appends optional Qualcomm debug support.

## State and Persistence Behavior

The file has no runtime state. Its build-time state determines which implementation hooks are linked into the kernel or module. Because `arm-smmu-nvidia.o` is unconditional inside `arm_smmu-objs`, NVIDIA implementation probing is compiled with the generic legacy driver whenever `CONFIG_ARM_SMMU` is enabled.

## Dependencies and Integration Points

The Makefile integrates the `drivers/iommu/arm/arm-smmu/` directory with Linux Kbuild and with Kconfig symbols. It must match prototypes and conditional calls in `arm-smmu.h` and `arm-smmu-impl.c`; for example, `arm-smmu-impl.c` can call `qcom_smmu_impl_init` only when the related config is enabled.

## Risks and Edge Cases

Build linkage is the main risk. Removing a file from `arm_smmu-objs` without guarding its referenced symbols can break all `CONFIG_ARM_SMMU` builds. Adding an implementation object unconditionally increases the baseline driver footprint and can expose missing dependency headers on non-target architectures. Conditional debug objects must remain tied to the correct parent support config.

## Test Signals

Useful validation is matrix build coverage for `CONFIG_ARM_SMMU`, `CONFIG_QCOM_IOMMU`, `CONFIG_ARM_SMMU_QCOM`, and `CONFIG_ARM_SMMU_QCOM_DEBUG` combinations. Link tests should verify the aggregate `arm_smmu` object contains the implementation init/exit paths expected by the core and that no stale object names remain after source renames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/Makefile -->
