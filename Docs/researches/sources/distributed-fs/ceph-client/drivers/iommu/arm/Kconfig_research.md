# sources/distributed-fs/ceph-client/drivers/iommu/arm/Kconfig

Purpose: Kconfig menu for Arm-family IOMMU drivers, including Arm SMMU v1/v2, Arm SMMU v3, Qualcomm IOMMU, SVA, iommufd, KUnit tests, and Tegra241 CMDQ-V.

Important symbols: `ARM_SMMU`, `ARM_SMMU_LEGACY_DT_BINDINGS`, `ARM_SMMU_DISABLE_BYPASS_BY_DEFAULT`, `ARM_SMMU_MMU_500_CPRE_ERRATA`, `ARM_SMMU_QCOM`, `ARM_SMMU_QCOM_DEBUG`, `ARM_SMMU_V3`, `ARM_SMMU_V3_SVA`, `ARM_SMMU_V3_IOMMUFD`, `ARM_SMMU_V3_KUNIT_TEST`, `TEGRA241_CMDQV`, and `QCOM_IOMMU`.

Control flow: build configuration selects the generic IOMMU API and io-pgtable backends, exposes optional subfeatures only under their parent driver, and gates SVA/iommufd/test source inclusion through the Makefiles. `ARM_SMMU_V3` selects `IOMMUFD_DRIVER` when IOMMUFD is enabled.

State and persistence: no runtime state; this file determines which code is compiled and which runtime capabilities can exist.

Dependencies and integration points: ties Arm drivers to `ARM64`, `ARM`, `COMPILE_TEST`, `IOMMU_API`, `IOMMU_IO_PGTABLE_LPAE`, `IOMMU_SVA`, `IOMMU_IOPF`, `MMU_NOTIFIER`, `KUNIT`, and Qualcomm SCM/ARM DMA helper selections.

Risks: incorrect dependency/select relationships can build unsupported feature combinations, especially SVA without notifier/IOPF support or KUnit without SVA symbols. Defaults like disabling unmatched bypass affect platform security posture.

Test signals: `allyesconfig`, `allmodconfig`, ARM64 defconfig, SVA/iommufd-enabled builds, and KUnit config builds should all resolve symbols consistently.
