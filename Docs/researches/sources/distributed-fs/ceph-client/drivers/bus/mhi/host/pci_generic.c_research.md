# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/pci_generic.c

## Purpose

`pci_generic.c` is the generic MHI-over-PCI controller driver for Qualcomm-style modems and related PCIe devices. It maps PCI device IDs to MHI controller configurations, claims PCI resources, wires MHI controller callbacks, registers and powers up the controller, handles EDL triggering, runtime/system PM, health-check recovery, PCI reset, AER recovery, and SR-IOV configuration.

## Important APIs, Types, And Functions

- Device description: `struct mhi_pci_dev_info` records controller config, optional VF config, firmware names, EDL image/trigger support, BAR, DMA width, MRU, sideband wake, M3 support, and reset-on-remove policy.
- Configuration macros build `struct mhi_channel_config` and `struct mhi_event_config` entries for UL, DL, SBL, FP, software data, control, and hardware event rings.
- PCI glue: `mhi_pci_claim()`, `mhi_pci_get_irqs()`, `mhi_pci_read_reg()`, `mhi_pci_write_reg()`, `mhi_pci_runtime_get()`, and `mhi_pci_runtime_put()`.
- Lifecycle: `mhi_pci_probe()`, `mhi_pci_remove()`, `mhi_pci_shutdown()`, `mhi_pci_reset_prepare()`, `mhi_pci_reset_done()`.
- Recovery and PM: `mhi_pci_recovery_work()`, `health_check()`, runtime suspend/resume, system suspend/resume, freeze/restore, and PCI error handlers.

## Control Flow

Probe selects the correct controller config for PF/VF, allocates `struct mhi_pci_device`, initializes recovery work and PF health timer, fills the embedded `struct mhi_controller`, claims PCI BAR and DMA mask, allocates MSI/MSI-X vectors, saves PCI state for recovery, registers the MHI controller, prepares MHI for power-up, and starts async MHI power-up. Runtime autosuspend is enabled only when PCI PME from D3hot and MHI M3 are supported.

When MSI vectors are scarce, `mhi_pci_get_irqs()` falls back to a shared MSI by rewriting each event config IRQ index to zero and setting `nr_irqs` to one. Health checks periodically read the physical function vendor ID; invalid reads queue recovery. Recovery powers down and unprepares MHI if it had started, restores PCI state, verifies liveness, prepares and synchronously powers up MHI, restarts the health timer, or attempts a PCI function reset on failure.

Runtime suspend stops the health timer and recovery work, transitions MHI to M3 if the device is started in AMSS, disables the PCI function, and enables D3 wake. Resume re-enables PCI, restores bus mastering and wake settings, exits M3, and restarts health checks. PCI AER and reset callbacks reuse the same MHI power-down/unprepare and recovery work patterns.

## State And Persistence Behavior

The embedded `mhi_controller` persists for the PCI device lifetime. `mhi_pci_device.status` holds `MHI_PCI_DEV_STARTED` and `MHI_PCI_DEV_SUSPENDED` bits. A saved PCI config snapshot is kept outside the PCI core's transient saved state for sudden error recovery. Timers and workqueues persist until remove/shutdown. Device tables are static, but some event config arrays are intentionally mutable because shared-MSI fallback patches IRQ fields.

## Dependencies And Integration Points

This driver integrates Linux PCI, PM runtime, timers, workqueues, MHI core APIs from `init.c`/`pm.c`, firmware names consumed by the MHI firmware loader, and child MHI client drivers for channels such as MBIM, QMI, DIAG, SAHARA, FIREHOSE, IP_SW, and IP_HW. It registers as `mhi-pci-generic` with a large `pci_device_id` table for Qualcomm, Quectel, Foxconn, Thales/Cinterion, Sierra, Telit, NetPrisma, and HP variants.

## Risks

Shared-MSI fallback mutates `event_cfg` through a `const struct mhi_controller_config *`, so configs backed by read-only memory would be unsafe; the current mutable event arrays are important. Runtime PM error recovery deliberately returns success after queuing async recovery to avoid destabilizing PCI state, which can hide failures except in logs. Health checks only run for physical functions. EDL trigger writes a magic cookie to channel doorbell 91 and resets the SoC; incorrect device matching or offset handling would be disruptive. Remove ordering must cancel timers/work before unregistering MHI to avoid use-after-free.

## Test Signals

Probe logs with the expected device name, successful BAR mapping, DMA mask setup, MSI allocation, MHI controller registration, channel device creation, and mission-mode uevents are primary signals. Exercise shared-MSI systems, PF/VF configs, runtime autosuspend/resume, D3hot wake, firmware crash callbacks, health-check-triggered recovery, AER reset, hibernation freeze/restore, EDL trigger sysfs, and reset-on-remove devices.
