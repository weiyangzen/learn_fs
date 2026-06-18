<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-impl.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-impl.c

## Purpose

`arm-smmu-impl.c` contains model-specific and platform-specific implementation quirks for the legacy Arm SMMU v1/v2 driver. It supplies alternate register accessors, reset hooks, context initialization hooks, feature masking, and implementation selection for Calxeda secure/non-secure register access, Cavium SMMUv2 erratum handling, Arm MMU-500 behavior, Marvell Armada AP806 MMU-500 access quirks, NVIDIA Tegra integration, and optional Qualcomm support.

## Important APIs, Types, and Functions

Calxeda support is implemented by `arm_smmu_gr0_ns`, `arm_smmu_read_ns`, `arm_smmu_write_ns`, and `calxeda_impl`, redirecting selected secure GR0 register offsets to non-secure aliases.

Cavium support uses `struct cavium_smmu`, `cavium_cfg_probe`, `cavium_init_context`, `cavium_impl`, and `cavium_smmu_impl_init`. It extends the base device allocation to store an `id_base` and offsets ASIDs/VMIDs per SMMU instance for erratum 27704.

MMU-500 support is centered on `arm_mmu500_reset` and `arm_mmu500_impl`. The reset hook clears ACR cache lock on r2p0+, enables unmatched stream ID/context-bank bypass TLB allocation, and optionally disables context-bank next-page prefetch with `CONFIG_ARM_SMMU_MMU_500_CPRE_ERRATA`.

Marvell support uses `mrvl_mmu500_readq`, `mrvl_mmu500_writeq`, `mrvl_mmu500_cfg_probe`, and `mrvl_mmu500_impl`. It splits 64-bit accesses into ordered 32-bit accesses and hides AArch64 page table format support to avoid erratum 582743.

Top-level entry points are `arm_smmu_impl_init`, `arm_smmu_impl_module_init`, and `arm_smmu_impl_module_exit`.

## Control Flow

`arm_smmu_impl_init` first selects model-specific implementation hooks by `smmu->model`. `ARM_MMU500` installs the MMU-500 reset implementation. `CAVIUM_SMMUV2` replaces the generic allocation with a `cavium_smmu` and installs Cavium hooks. It then checks platform integration quirks by device-tree compatibility or property: Calxeda secure-config access installs non-secure register accessors; NVIDIA Tegra compatible strings delegate to `nvidia_smmu_impl_init`; Qualcomm support is initialized when configured; Marvell AP806 installs Marvell access and reset hooks. The function returns the original or replacement `arm_smmu_device`.

Module init/exit only forward to Qualcomm module hooks when `CONFIG_ARM_SMMU_QCOM` is enabled. This keeps the generic implementation file as the central dispatcher without making Qualcomm support mandatory.

## State and Persistence Behavior

Most state is static hook tables. Cavium allocates a larger device structure containing `id_base`; `cavium_cfg_probe` uses a static atomic `context_count` to ensure unique ASID/VMID windows across SMMUs. MMU-500 and Marvell hooks persist by assigning `smmu->impl`. Calxeda and Marvell register accessor changes affect all later reads/writes through the legacy driver's `arm_smmu_*` access wrappers.

Hardware state changes occur in reset/config hooks: MMU-500 ACR/ACTLR fields are modified, Marvell feature bits are masked before page table format selection, and Cavium ASID/VMID offsets alter context bank programming. There is no filesystem persistence.

## Dependencies and Integration Points

The file depends on `arm-smmu.h`, device-tree matching, bitfield helpers, and optional Qualcomm/NVIDIA implementation prototypes from the legacy SMMU header. It is linked into the `arm_smmu` object by the local Makefile. It integrates with the legacy driver through `struct arm_smmu_impl`, whose members include register accessors, reset, config probe, init context, and platform finalize hooks.

## Risks and Edge Cases

Implementation selection order matters. Model quirks are installed first so platform integration quirks can inherit or override them. A later assignment such as Marvell replacing `smmu->impl` can discard previously selected MMU-500 hooks unless the replacement table includes equivalent reset behavior, which this file does for Marvell.

Cavium ID offsetting depends on `num_context_banks` and a global atomic count. Incorrect ordering or reuse across hotplug paths could produce overlapping ASID/VMID allocations. Calxeda register remapping only covers selected GR0 secure registers; missing an offset would leave access to the wrong security alias.

MMU-500 CPRE errata handling depends on secure firmware clearing SACR cache lock; the driver warns if ACTLR writes do not stick. Marvell disables AArch64 formats to work around access-width restrictions, which can reduce functionality on affected systems.

## Test Signals

Build tests should cover Qualcomm configured and unconfigured, MMU-500 CPRE errata on/off, and NVIDIA support linked through the unconditional object. Runtime or emulated tests should exercise implementation selection for each compatible/model, verify Calxeda non-secure offset remapping, Cavium ASID/VMID offset uniqueness, MMU-500 ACR/ACTLR reset writes and warning path, Marvell split 64-bit accessors, and preservation of reset hooks when platform quirks override model hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-impl.c -->
