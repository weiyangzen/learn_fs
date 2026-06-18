# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/Makefile

Purpose: Kbuild rules for the Arm SMMU v3 driver and optional companion objects.

Important build entries: `obj-$(CONFIG_ARM_SMMU_V3) += arm_smmu_v3.o`; base object list `arm_smmu_v3-y := arm-smmu-v3.o`; optional additions for `CONFIG_ARM_SMMU_V3_IOMMUFD`, `CONFIG_ARM_SMMU_V3_SVA`, and `CONFIG_TEGRA241_CMDQV`; separate KUnit module/object `obj-$(CONFIG_ARM_SMMU_V3_KUNIT_TEST) += arm-smmu-v3-test.o`.

Control flow: Kbuild links optional iommufd/SVA/CMDQ-V code into the main SMMU v3 object when enabled, while tests are built independently under the KUnit config.

State and persistence: no runtime state.

Dependencies and integration points: mirrors `arm/Kconfig` feature symbols and determines whether functions such as SVA domain allocation or iommufd vSMMU hooks are present in the driver binary.

Risks: missing an optional object here produces unresolved callbacks or disabled features despite Kconfig enabling them. Test object dependencies must match exported-for-KUnit symbols from the core driver.

Test signals: compile matrix for base SMMU v3, SVA, iommufd, Tegra CMDQ-V, and KUnit combinations.
