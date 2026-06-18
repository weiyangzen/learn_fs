# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/pci.c

## Purpose

`pci.c` is the ath10k PCIe/AHB host-interface implementation for Qualcomm Atheros 802.11ac devices. It owns PCI probe/remove, BAR mapping, DMA setup, Copy Engine pipe configuration, firmware boot configuration, BMI transport, diagnostic memory access, interrupt/NAPI handling, power-save wake/sleep, firmware crash dumps, chip reset sequences, EEPROM calibration fetch, suspend/resume, and module registration.

## Important APIs, Types, and Functions

- Module parameters `irq_mode` and `reset_mode` constrain interrupt and reset behavior.
- `ath10k_pci_id_table` and `ath10k_pci_supp_chips` identify and validate supported devices/revisions.
- `pci_host_ce_config_wlan[]`, `pci_target_ce_config_wlan[]`, and `pci_target_service_to_ce_map_wlan[]` define host CE rings, firmware CE configuration, and HTC service-to-pipe mappings.
- MMIO helpers include `ath10k_pci_read32()`, `ath10k_pci_write32()`, `ath10k_pci_soc_*()`, and `ath10k_pci_reg_*()`.
- HIF APIs include `ath10k_pci_hif_tx_sg()`, `ath10k_pci_hif_diag_read()`, `ath10k_pci_diag_write_mem()`, `ath10k_pci_hif_exchange_bmi_msg()`, service-to-pipe mapping, send-complete polling, HIF start/stop, and HIF power-up/down.
- Resource helpers allocate/init/free CE pipes, RX buffers, NAPI, IRQs, and PCI resources.
- Reset helpers implement warm/cold/chip-specific reset paths and target-init waits.
- Crash helpers collect firmware register and memory dumps and start ath10k recovery.
- `ath10k_pci_probe()` and `ath10k_pci_remove()` are the PCI driver entry points.

## Control Flow

Probe maps the PCI ID to hardware revision, power-save policy, reset callbacks, and target-address translation. It creates ath10k core state, initializes PCI private state, allocates CE resources, claims BAR0 with a 32-bit DMA mask, wakes the device, disables stale interrupts/CE state, initializes IRQ/NAPI, requests IRQ, resets the chip, validates chip ID, and registers ath10k core.

HIF power-up disables ASPM, resets the chip, initializes CE pipes, writes target CE/service-map configuration through diagnostic CE, sets firmware early allocation flags, and wakes the target CPU. HIF start enables NAPI/interrupts, posts RX buffers, and restores saved ASPM bits. HIF stop disables and synchronizes interrupts, disables NAPI, cancels dump work, resets the chip to stop DMA, flushes timers and CE buffers, and checks wake references.

TX submits SG items to CE rings under `ce_lock`, using gather flags for all but the final segment and reverting descriptors on failure. RX posts DMA-mapped skbs to CE destination rings, drains completions in CE callbacks, validates lengths, invokes HTC/HTT/pktlog handlers, and reposts or recycles buffers. Interrupts wake the device, filter shared INTx, mask/clear sources, and schedule NAPI; NAPI services CE/HTT work and unmasks when the budget is not exhausted.

Diagnostic and BMI paths use DMA bounce buffers, CE send/receive polling, timeouts, and explicit cleanup. Reset flow is chip-specific: QCA988X prefers warm reset with cold fallback, QCA6174 uses cold then warm reset, and QCA99X0-style chips use cold reset.

## State and Persistence Behavior

Long-lived state lives in `struct ath10k_pci`: PCI device/BAR, IRQ mode, CE pipes, diagnostic CE, work/timers, CE config arrays, saved link control, power-save refcount/awake cache, and reset/address callbacks. The file also mutates CE rings and DMA mappings, firmware host-interest memory, IRQ/MSI/NAPI registration, ath10k crash/reset stats, and core registration state. No user persistent files are written; firmware names are declared with `MODULE_FIRMWARE()`.

## Dependencies and Integration Points

The file depends on Linux PCI, DMA, IRQ, NAPI, timer, workqueue, module, and PM APIs. ath10k dependencies include core, debug, coredump, target-address, BMI, HIF, HTC, CE, and PCI headers. It exposes `ath10k_hif_ops` to ath10k core and integrates CE callbacks with HTC/HTT/WMI data paths.

## Risks and Edge Cases

- Wake/sleep refcounting is critical; MMIO while asleep can return invalid values or corrupt host memory.
- Diagnostic CE and BMI polling use fixed timeouts and can fail boot/recovery on firmware stalls.
- RX retry timers must be deleted before CE/skb teardown.
- INTx/MSI masking has chip-specific gaps for QCA99X0-style firmware interrupt masking.
- Warm reset comments document CE recovery and host-hang risks.
- QCA6174/QCA9377 CE5 overrides are sensitive to firmware service mapping.
- EEPROM calibration is QCA9887-specific and checksum-gated.

## Test Signals

- Probe/remove across supported IDs should verify BAR, DMA, IRQ, NAPI, CE, and core lifecycle.
- Boot tests should trace target init, CE config writes, BMI, HIF start, and firmware service readiness.
- MSI/INTx tests should cover shared IRQ filtering, NAPI pending-race handling, crash indication, and IRQ teardown.
- Fault injection should target DMA mapping, skb allocation, CE ring full, diagnostic timeout, MSI enable failure, reset failure, and calibration read failure.
- Recovery tests should verify crash dumps, safe reset, CE cleanup, and no DMA leaks.
