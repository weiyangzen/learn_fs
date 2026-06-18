# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/pci.c

## Purpose
Provides small shared PCIe ASPM helpers for mt76 PCI drivers. The file lets chip drivers detect whether ASPM is active and force-disable L0s/L1 link power states when hardware or firmware requires more stable PCIe latency.

## Important APIs, Types, And Functions
`mt76_pci_disable_aspm()` reads the device and parent link-control ASPM fields, logs the active ASPM modes, calls `pci_disable_link_state()` when PCIEASPM core support is available, and falls back to clearing device and parent `PCI_EXP_LNKCTL` ASPM bits. `mt76_pci_aspm_supported()` returns whether either endpoint or upstream link currently advertises active ASPM bits.

## Control Flow
Both helpers read the device link-control register and, when present, the parent bridge link-control register. Disable exits early if neither side has ASPM enabled. Otherwise it tries the kernel PCIe ASPM API first; only if that fails or is unavailable does it directly clear ASPM bits in the downstream component then upstream component.

## State And Persistence
The only persistent state affected is PCIe link-control configuration in the endpoint and parent bridge. No mt76-private state is stored.

## Dependencies And Integration Points
Depends on Linux PCIe capability helpers, `pci_disable_link_state()`, `CONFIG_PCIEASPM`, and callers in PCI mt76 chip drivers that decide when ASPM must be disabled or probed.

## Risks
Directly clearing parent/device ASPM bits can affect power behavior beyond the mt76 function. Parent and child settings must remain consistent. The helper only considers current L0s/L1 bits, not policy state or platform firmware expectations.

## Test Signals
Driver probe on PCIe devices with ASPM enabled/disabled, logs showing disabled L0s/L1, stable DMA and firmware command behavior after disabling, and no PCIe AER/link errors or suspend/resume regressions.
