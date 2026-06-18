# sources/distributed-fs/ceph-client/drivers/iommu/arm/Makefile

Purpose: delegates Arm IOMMU builds to the `arm-smmu/` and `arm-smmu-v3/` subdirectories.

Important build entries: `obj-y += arm-smmu/ arm-smmu-v3/` ensures both subdirectory Makefiles are visited regardless of whether their contained objects are selected.

Control flow: Kbuild descends into both folders, where config-dependent object variables decide actual compilation.

State and persistence: no runtime state.

Dependencies and integration points: integrates this directory into the parent `drivers/iommu` build and relies on subdirectory Makefiles to honor Kconfig symbols.

Risks: removing a subdirectory here would silently omit its driver even if Kconfig enables it. Adding config gating here could diverge from subdirectory selection.

Test signals: Kbuild traversal under configs with only SMMU v1/v2, only SMMU v3, or neither should remain clean.
