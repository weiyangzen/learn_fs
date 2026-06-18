# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pcic.h

Purpose: Declares the PCI-common ath11k interface and shared PCI window/IRQ constants used by PCI HIF and related modules.

Important APIs and constants: IRQ offsets define CE IRQ base `ATH11K_PCI_IRQ_CE0_OFFSET`, DP IRQ base `ATH11K_PCI_IRQ_DP_OFFSET`, and the special CE wake IRQ. Window constants define enable bit, selector register, value mask, window start, window range mask, and the always-accessible BAR offset threshold. Public functions cover MSI assignment/address lookup, register read/write/range read, CE MSI index calculation, IRQ config/free/start/stop, external IRQ enable/disable, CE IRQ enable/disable-sync, MSI config selection, PCI ops registration, service-to-pipe mapping, and wake-IRQ-preserving CE IRQ toggles.

Control flow: Bus-specific PCI code registers mandatory PCI ops, initializes MSI config, configures IRQs, and exposes these helpers through HIF ops. MHI asks for the MHI MSI assignment. QMI/HTC code maps services to CE pipes. Power and recovery paths use start/stop and selective CE IRQ helpers.

State and persistence behavior: The header has no state but defines stable offsets and function contracts that mutate `ath11k_base` PCI/IRQ/CE/DP state. The window constants define how high register offsets are mapped through BAR window selection.

Dependencies and integration points: Includes ath11k core definitions and depends on bus-specific `ath11k_pci_ops` being present in `ab->pci.ops`. Integrates with Linux IRQ/NAPI through the implementation and with MHI/QMI/HIF through exported functions.

Risks and edge cases: Offset constants must match hardware and `irq_name`/MSI layouts. Callers must not use register helpers before PCI ops are registered. Range reads use inclusive `start`/`end` and assume 32-bit alignment. Selective CE IRQ helpers must keep the wake IRQ enabled/disabled as intended during WoW or low-power flows.

Test signals: Compile all declaration users, validate register window access above and below the always-accessible range, verify MHI/CE/DP MSI assignment for each hardware revision, and exercise CE IRQ except-wake helpers in suspend/resume scenarios.
