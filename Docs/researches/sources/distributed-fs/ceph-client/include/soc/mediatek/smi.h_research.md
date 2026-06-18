# sources/distributed-fs/ceph-client/include/soc/mediatek/smi.h

Purpose: exposes MediaTek SMI/IOMMU integration definitions for local arbiter IOMMU configuration.

Important APIs and types: under `CONFIG_MTK_SMI`, `enum iommu_atf_cmd` defines secure monitor commands to configure SMI LARB or infra IOMMU. `MTK_SMI_MMU_EN(port)` builds an enable bit for a port. `struct mtk_smi_larb_iommu` records a LARB device, MMU bitmask, and per-port bank mapping.

Control flow: MediaTek IOMMU/SMI code associates LARB devices with ports/banks, computes MMU enable bits, and may issue ATF commands to enable or disable IOMMU paths for multimedia or infrastructure masters.

State and persistence: runtime state is LARB device association, MMU masks, bank routing, and secure firmware configuration. No persistent storage is managed.

Dependencies and integration points: depends on bitops and device headers and is compiled only for MediaTek SMI users. Integrates IOMMU, SMI bus, multimedia, and ATF firmware paths.

Risks and test signals: risks include missing declarations when `CONFIG_MTK_SMI` is disabled, wrong port-to-bank mapping, secure firmware command mismatch, and enabling untranslated DMA. Test LARB probe, IOMMU attach/detach, per-port enable bits, multimedia DMA under IOMMU, and disabled-config compile paths.
