# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/pci.c

## Purpose

`pci.c` is the HIF/bus implementation for PCI ath12k devices. It claims and maps BAR0, manages register windowing, allocates MSI vectors, configures CE and DP interrupts, initializes QMI CE configuration, powers firmware through MHI, handles reset and coredump paths, implements probe/remove/shutdown/PM callbacks, and exposes registration for device-family-specific PCI drivers.

## Important APIs And Functions

- Register access: `ath12k_pci_read32()` and `ath12k_pci_write32()` handle low BAR offsets, dynamic/static window selection, MHI region special casing, optional wake/release callbacks, and export read access.
- IRQ setup: `ath12k_pci_msi_alloc()`, `ath12k_pci_get_user_msi_assignment()`, `ath12k_pci_config_irq()`, CE IRQ handlers/workqueues, DP ext IRQ handlers, and NAPI polling bridge MSI vectors to CE and datapath rings.
- Power/reset: `ath12k_pci_sw_reset()`, `ath12k_pci_soc_global_reset()`, `ath12k_pci_power_up()`, and `ath12k_pci_power_down()` sequence LTSSM, interrupt clear, vector clear, debug register clear, MHI reset, ASPM, MSI, QRTR node ID, and MHI state.
- HIF ops: `ath12k_pci_hif_ops` wires start/stop/read/write/power/PM/IRQ/MSI/service-to-pipe/coredump callbacks into core.
- Probe/remove: `ath12k_pci_probe()` allocates core state, claims PCI resources, discovers device-family ops, allocates MSI, pre-inits core, registers MHI, initializes HAL SRNG/CE/IRQs, runs arch init, then starts ath12k core. `ath12k_pci_remove()` unwinds QMI/core/MHI/IRQ/MSI/BAR/HAL/CE resources.
- Device-family module API: `ath12k_pci_register_driver()` and `ath12k_pci_unregister_driver()` maintain the family driver table and register a real `pci_driver`.

## Control Flow

Probe is linear with labeled error unwinds. After resources are claimed, MHI is registered before HAL/CE IRQs, because firmware boot later depends on MHI. Core power-up calls HIF `power_up`, which resets hardware, disables ASPM for firmware download, enables MSI, writes a unique QRTR node when needed, starts MHI synchronously, and optionally selects static windows. Runtime `start` marks init done, restores ASPM for multi-vector devices, enables CE IRQs, and posts RX buffers. Interrupt flow disables the IRQ source, services CE in a bottom-half workqueue or DP rings through NAPI, then re-enables interrupts after work completes.

## State And Persistence

State lives in `struct ath12k_pci`: PCI device, BAR/register window cache, MSI base data and flags, MHI controller, qmi instance, DMA mask, ASPM link control backup, family ops, and register bases. Device flags track CE/DP IRQ enable and init state. There is no disk persistence, but coredump code assembles a vmalloc crash artifact from MHI FBC/RDDM images and QMI target memory, then queues devcoredump work.

## Dependencies And Integration

The file depends on Linux PCI/MSI/IRQ/NAPI/PM/vmalloc APIs and ath12k core, HIF, MHI, HAL, CE, DP, QMI, and debug infrastructure. It is the integration point between generic ath12k core and family-specific PCI modules such as QCN9274/WCN7850.

## Risks And Test Signals

Risks include BAR window races, incorrect MSI fallback behavior, IRQ leaks on partial probe failure, ASPM/MHI resume interactions, reset timing uncertainty, QRTR instance collisions on multi-device systems, and coredump size/copy errors. Test signals include module probe/remove under every supported family, one-MSI and multi-MSI operation, CE/DP traffic under NAPI, suspend/resume, firmware recovery, devcoredump generation, service-to-pipe mapping, register access across static/dynamic windows, and fault-injection of each probe error label.
