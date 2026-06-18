# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ahb.c

## Purpose
`ahb.c` is the platform-bus host interface for ath11k SoCs exposed through device tree compatibles such as `qcom,ipq8074-wifi`, `qcom,ipq6018-wifi`, `qcom,ipq5018-wifi`, and hybrid WCN6750. It binds a `platform_driver`, selects AHB or PCIC-style HIF operations, maps device resources, boots the Q6 remote processor, configures firmware memory, and wires copy-engine and datapath interrupts into the ath11k core.

## Important APIs, Types, And Functions
The file owns `ath11k_ahb_probe()`, `ath11k_ahb_remove()`, and `ath11k_ahb_shutdown()` for driver lifecycle. `ath11k_ahb_hif_ops_ipq8074` supplies direct MMIO read/write, CE/ext IRQ enable/disable, service-to-pipe mapping, and remoteproc power control. `ath11k_ahb_hif_ops_wcn6750` delegates most register and IRQ work to PCIC helpers while keeping AHB remoteproc power and SMP2P suspend/resume. IRQ setup is split across `ath11k_ahb_config_irq()`, `ath11k_ahb_config_ext_irq()`, CE tasklets, and NAPI polling. Resource paths include `ath11k_ahb_setup_resources()`, `ath11k_ahb_ce_remap()`, `ath11k_ahb_fw_resources_init()`, `ath11k_ahb_setup_msi_resources()`, and `ath11k_ahb_setup_smp2p_handle()`.

## Control Flow
Probe reads the matched hardware revision, allocates `ath11k_base` with AHB private storage, registers optional PCI ops, initializes hardware params, maps MMIO or MSI resources, remaps CE space when required, initializes fixed firmware memory/IOMMU mappings, sets SMP2P handles, initializes HAL SRNG, allocates CE pipes, fills QMI CE config, obtains the remoteproc, initializes core services, requests IRQs, and triggers QMI cold-boot reset handling. Runtime start enables CE interrupts and posts CE RX buffers. External datapath IRQs disable their group, schedule NAPI, service SRNGs through `ath11k_dp_service_srng()`, then re-enable IRQs after budget completion. Removal waits for recovery if needed, marks unregistering, cancels restart/QMI work, deinitializes core, destroys firmware state, frees IRQs, SRNGs, SMP2P handles, IOMMU mappings, CE pipes, and core memory.

## State And Persistence
State is held in `ath11k_base` plus `struct ath11k_ahb` private data: remoteproc handle, firmware memory addresses/sizes, IOMMU domain, firmware platform device, TrustZone-vs-IOMMU selection, and SMP2P state. IRQ numbers are cached in `ab->irq_num`, and ext IRQ group membership is derived from hardware ring masks. There is no persistent storage, but the driver consumes device tree memory regions and optional firmware child nodes.

## Dependencies And Integration Points
This file integrates with Linux platform, OF, reserved memory, IOMMU, DMA mapping, remoteproc, qcom SMEM state, NAPI, tasklets, HAL SRNG, CE, QMI, HIF, PCIC, and DP. It is tightly coupled to `core.c` initialization and `ce.c` buffer posting/cleanup.

## Risks And Test Signals
Risk concentrates around error unwinding, IRQ lifecycle, and platform description correctness. `ath11k_ahb_config_ext_irq()` logs request failures but continues, so missing IRQs can surface later as stalled rings. Fixed firmware memory setup has multi-step IOMMU/platform-device unwind paths. Suspend/resume depends on `device_may_wakeup()`, wake IRQ selection, SMP2P sequence updates, and wake completion timing. Useful test signals include successful probe/unprobe on all compatibles, IRQ storm/stall checks under traffic, firmware boot/restart, WoW suspend/resume on WCN6750, and fault injection in IOMMU, remoteproc, and IRQ request paths.
