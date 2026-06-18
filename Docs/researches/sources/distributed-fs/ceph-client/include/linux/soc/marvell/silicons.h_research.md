# sources/distributed-fs/ceph-client/include/linux/soc/marvell/silicons.h

Purpose: This header names Marvell silicon IDs or families for shared use across Marvell platform and driver code.

Important APIs/types/functions: On ARM64 it defines `CN20K_CHIPID` as `0x20` and inline `is_cn20k(struct pci_dev *pdev)`, which tests the low byte of `pdev->subsystem_device`. Non-ARM64 builds define `is_cn20k(pdev)` as a false expression that consumes the argument.

Control flow: PCI-backed Marvell drivers call `is_cn20k` during probe or quirk selection to choose CN20K-specific behavior.

State and persistence: No state is stored. The helper interprets PCI subsystem device IDs supplied by hardware/firmware.

Dependencies and integration: Includes Linux types and PCI definitions. Integrates with Marvell PCI device drivers that support multiple silicon families.

Risks and test signals: A wrong subsystem-device interpretation can select incompatible queue/register behavior. Test CN20K and non-CN20K PCI devices, ARM64/non-ARM64 builds, and all call sites that gate quirks on `is_cn20k`.
