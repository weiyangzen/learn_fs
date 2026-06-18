# sources/distributed-fs/ceph-client/drivers/scsi/isci/init.c

## Purpose

`init.c` is the module, PCI, libsas, and SCSI-host registration layer for the Intel C600 SAS `isci` driver. It defines supported PCI IDs, module parameters, SCSI host template, libsas domain callbacks, PCI probe/remove, suspend/resume, host allocation, OEM parameter loading, and module init/exit.

## Important APIs, Types, and Functions

Module registration uses `isci_init()` and `isci_exit()`, a `pci_driver` named `isci`, and firmware declaration `MODULE_FIRMWARE(ISCI_FW_NAME)`. Supported devices are listed in `isci_id_table`. Module parameters include `no_outbound_task_to`, `ssp_max_occ_to`, `stp_max_occ_to`, `ssp_inactive_to`, `stp_inactive_to`, `phy_gen`, `max_concurr_spinup`, and `cable_selection_override`.

The SCSI surface is `isci_sht`, built from `LIBSAS_SHT_BASE`, with `scan_finished = isci_host_scan_finished`, `scan_start = isci_host_start`, queue depth, SG size, abort handler, host attributes, ATA sdev attributes, and DIF/DIX support enabled during host allocation. The libsas callback table `isci_transport_ops` wires port formed/deformed, device found/gone, execute task, task management, ATA readiness, nexus clear, phy control, and GPIO write callbacks to sibling driver files.

PCI and allocation helpers include `isci_register_sas_ha()`, `isci_unregister()`, `isci_pci_init()`, `num_controllers()`, `isci_setup_interrupts()`, `isci_user_parameters_get()`, `sci_user_parameters_set()`, `sci_oem_defaults()`, `isci_host_alloc()`, `isci_pci_probe()`, `isci_pci_remove()`, `isci_suspend()`, and `isci_resume()`.

## Control Flow

Module init attaches a SAS transport template using `isci_transport_ops` and registers the PCI driver. Probe allocates `isci_pci_info`, tries OEM parameter sources in priority order (EFI variable, option ROM, then request_firmware), validates any discovered per-controller parameters, initializes PCI BARs and DMA masks, allocates one or two `isci_host` objects based on BAR size, sets up MSI-X or shared INTx interrupts, and starts SCSI scanning for each host.

`isci_host_alloc()` initializes locks, waitqueues, tasklet, libsas host pointers, default/user/OEM parameters, ports, phys, and remote-device list heads. It allocates a `Scsi_Host`, calls `isci_host_init()` to initialize hardware/private state, attaches the SAS transport, sets host addressing and command limits, enables DIF/DIX guard support, adds the SCSI host, and registers the libsas HA. On failures it removes or drops the partially allocated SCSI host.

Interrupt setup first requests the exact MSI-X vector count, two vectors per controller, with even vectors for completions and odd vectors for errors. If MSI-X allocation or IRQ request fails, it frees any partial MSI-X setup and falls back to shared INTx, registering one handler per host on vector zero. Remove waits for host start, unregisters the SAS HA/SCSI host, and deinitializes hardware. Suspend unregisters active hardware state after `sas_suspend_ha()`; resume prepares libsas, reinitializes hardware, restarts the host, waits for start, and resumes libsas.

## State and Persistence Behavior

Persistent driver configuration is via module parameters and optional platform/firmware OEM data. Runtime state is allocated with devm-managed memory under the PCI device and normal SCSI host references. `pci_info->orom` stores the selected OEM parameter block for host allocation. The sysfs `isci_id` attribute exposes the per-controller ID. No on-disk state is written by this file.

## Dependencies and Integration Points

The file depends on Linux module, PCI, firmware, EFI runtime variable support, DMA mask APIs, SCSI host registration, libsas transport registration, SAS ATA attributes, tasklet setup, and power-management hooks. Internal integration points include `host.h`, `task.h`, `probe_roms.h`, port/device/task/phy functions declared in sibling headers, and the firmware file name from `probe_roms.h`.

## Risks and Edge Cases

OEM parameter source fallback is subtle: invalid option ROM entries discard the whole ROM path and fall back to firmware/defaults. `isci_host_alloc()` checks `id > orom->hdr.num_elements`, which should be reviewed with the ROM element count semantics because off-by-one validation could read an invalid controller slot. MSI-X setup requests an exact vector count; systems unable to provide it immediately fall back to INTx. Probe calls `scsi_scan_host()` after interrupts are registered, so host start and scan completion depend on `IHOST_START_PENDING` clearing even on start timeout. Resume assumes `isci_host_init()` and `isci_host_start()` restore enough hardware state before `sas_resume_ha()`.

## Test Signals

Validation signals include module load printing version `1.2.0`, PCI probe for all listed Intel device IDs, correct one-versus-two controller detection by BAR size, OEM parameter source messages, fallback to default SAS addresses when firmware is absent, MSI-X and INTx interrupt paths both working, `isci_id` sysfs values per host, SCSI scan delayed until controller start completes, libsas device discovery, and suspend/resume preserving the SAS domain.
