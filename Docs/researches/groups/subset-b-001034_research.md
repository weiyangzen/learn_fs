# Research: subset-b-001034

Grouped research for ATA/libata PCI, AHCI, platform-AHCI, and ACPI integration sources. Each section preserves the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ata_generic.c -->
# sources/distributed-fs/ceph-client/drivers/ata/ata_generic.c

## Purpose
`ata_generic.c` is a fallback PCI IDE/PATA-style libata driver for controllers that implement the standard bus-mastering IDE interface but do not have a more specific native driver. Its central policy is conservative: trust firmware/BIOS programming, do not retune timing registers, and only bind broad IDE-class devices when the `all_generic_ide` module parameter permits it or when the device is known to be safe for this generic path.

## Important APIs, Types, And Functions
The driver registers `ata_generic_pci_driver` through `module_pci_driver()`, using `ata_generic[]` as its PCI ID table and `ata_generic_init_one()` as probe. `generic_sht` uses `ATA_BMDMA_SHT(DRV_NAME)`, and `generic_port_ops` inherits `ata_bmdma_port_ops` while overriding `set_mode` with `generic_set_mode()` and returning unknown cable type. The local flags `ATA_GEN_CLASS_MATCH`, `ATA_GEN_FORCE_DMA`, and `ATA_GEN_INTEL_IDER` encode match-entry behavior. The `all_generic_ide` module parameter controls whether broad IDE class matches are claimed.

`generic_set_mode()` is the key behavior hook. It inspects existing bus-master DMA status bits or forces DMA for known hardware, then fills libata device mode fields to match the firmware-enabled state. `is_intel_ider()` distinguishes Intel IDE-R virtual devices from ordinary Intel IDE controllers by probing PCI config offsets `0xf8` and `0x40`.

## Control Flow
Probe first rejects broad class matches unless `all_generic_ide` is set. Intel IDE-class matches are accepted only for IDE-R unless generic claiming is forced. UMC and OPTi multi-function devices skip function zero, disabled I/O decode devices are ignored, ALi simplex state is cleared, and ATI devices are explicitly enabled/pinned before handing off to `ata_pci_bmdma_init_one()`.

During mode setup, the driver obtains the PCI match entry from `ap->host->private_data`. If the match requested forced DMA, both device DMA bits are considered enabled. Otherwise, when a BMDMA register window exists, it reads `ATA_DMA_STATUS` and uses bits 5 and 6 for master/slave DMA enable state. For each enabled ATA device, the driver records baseline PIO/MWDMA capabilities, chooses DMA mode from the IDENTIFY transfer mask if DMA is firmware-enabled, or marks the device PIO-only when the bit is absent.

## State And Persistence
The file has no durable storage. Runtime state is held in libata device fields (`pio_mode`, `dma_mode`, `xfer_mode`, `xfer_shift`, `ATA_DFLAG_PIO`) and PCI config or MMIO status observed at probe/configuration time. The `all_generic_ide` module parameter is process/module state. ATI devices are pinned after `pcim_enable_device()` so managed cleanup does not disable them while the driver owns them.

## Dependencies And Integration Points
The file depends on PCI core matching, libata BMDMA helpers, SCSI host template plumbing, ATA IDENTIFY transfer-mask helpers, and legacy PCI vendor/device constants. It integrates below the SCSI/libata block stack as a low-level host driver and intentionally defers timing programming to firmware.

## Risks And Edge Cases
The generic driver can conflict with chipset-specific drivers if broad class matching is enabled too aggressively. `generic_set_mode()` assumes firmware-configured DMA bits are meaningful; stale or incorrect BIOS state can make libata believe DMA is safe when timing is not. The Intel IDE-R detection writes PCI config word `0x40` as a probe, so false positives/negatives around unusual Intel devices are sensitive. Rejecting disabled I/O decode avoids waking unused controllers but can miss devices that firmware left disabled.

## Test Signals
Useful signals include PCI probe logs with and without `all_generic_ide`, Intel IDE-R versus normal Intel IDE class devices, devices with BMDMA absent/present, DMA-status master/slave bit combinations, ATI pin-device behavior, and boot comparisons against chipset-specific ATA drivers. Runtime validation should include PIO-only fallback, DMA I/O correctness, suspend/resume through `ata_pci_device_suspend/resume`, and no binding when I/O decode is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ata_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ata_piix.c -->
# sources/distributed-fs/ceph-client/drivers/ata/ata_piix.c

## Purpose
`ata_piix.c` is the Intel PIIX/ICH low-level libata driver for legacy Intel PATA and IDE-mode SATA controllers, plus selected virtualized variants. It programs PCI configuration timing registers for PATA, maps IDE-mode SATA ports onto libata ports, exposes optional SIDPR SCR access for newer ICH controllers, and encodes many platform and firmware quirks needed for older Intel chipsets.

## Important APIs, Types, And Functions
The driver registers `piix_pci_driver` through explicit `module_init()`/`module_exit()` so it can use `in_module_init` to reject hotplug of later SATA devices after initial module load. `piix_pci_tbl[]` maps PCI IDs to `enum piix_controller_ids`; `piix_port_info[]` maps those IDs to libata masks, flags, and port operations. `struct piix_map_db` describes SATA map register decoding; `struct piix_host_priv` stores the decoded SATA map, saved IOCFG register, and optional SIDPR MMIO pointer.

Important operations include `piix_set_timings()`, `piix_set_piomode()`, `do_pata_set_dmamode()`, `ich_pata_cable_detect()`, `piix_init_sata_map()`, `piix_init_sidpr()`, `piix_disable_ahci()`, `piix_check_450nx_errata()`, `piix_iocfg_bit18_quirk()`, `piix_ignore_devices_quirk()`, `piix_init_one()`, and `piix_remove_one()`. Port operation variants cover PATA, ICH PATA, SATA, VMware PATA, and SIDPR-capable SATA.

## Control Flow
Probe copies the selected `ata_port_info` into two host ports, enables the PCI device with managed PCI helpers, allocates `piix_host_priv`, and saves `PIIX_IOCFG` before any ACPI or quirk path can alter it. ICH6R AHCI-capable devices are forced out of AHCI mode through BAR5 `HOST_CTL` before libata setup. SATA controllers decode `ICH5_PMR` through the chipset-specific map table, possibly converting an IDE channel to PATA port info or marking slave devices possible.

After `ata_pci_bmdma_prepare_host()`, SATA probe enables PCS bits, tests and installs SIDPR SCR access when BAR5 index/data registers are usable, applies the Clevo IOCFG bit-18 quirk, re-enables INTx for controllers that need it, disables DMA masks on affected 450NX systems, enables parallel scan, applies Hyper-V ATA-ignore policy when requested, sets PCI bus master, and activates the host with `ata_pci_sff_activate_host()`. Removal restores saved IOCFG before delegating to `ata_pci_remove_one()`.

PATA mode programming uses PCI config registers under `piix_lock`. PIO setup writes master timing registers at `0x40/0x42`, the separate slave timing register at `0x44`, sets SITRE, and clears UDMA enable bits. DMA setup either programs UDMA enable/timing/clock fields at `0x48`, `0x4a`, and ICH `0x54`, or derives MWDMA from matching PIO timings. SATA SIDPR SCR access selects port/PMP/register through BAR5 index and reads/writes BAR5 data; LPM delegates to `sata_link_scr_lpm()`.

## State And Persistence
Persistent hardware state lives in PCI config space: IOCFG, PMR, PCS, timing, UDMA, INTx, and optional AHCI-global-control registers. The driver saves IOCFG in `hpriv->saved_iocfg` and restores it on remove because ACPI `_STM` can disturb cable bits. Runtime state includes decoded SATA maps, SIDPR MMIO mappings, host flags such as `PIIX_HOST_BROKEN_SUSPEND`, libata port masks, and module parameters `prefer_ms_hyperv` and `in_module_init`.

## Dependencies And Integration Points
The file depends on PCI, DMI, libata SFF/BMDMA helpers, tracepoints for BMDMA status, ACPI-sensitive suspend/resume helpers, and SCSI host registration. It integrates with old IDE-mode Intel firmware assumptions, platform DMI quirk databases, Hyper-V storage preference logic, and optional SATA SCR/LPM sysfs support through SIDPR-specific shost attributes.

## Risks And Edge Cases
The code is quirk-heavy. Incorrect PCI ID mapping or map-table decoding can expose nonexistent ports or hide real devices. Timing register writes are shared across master/slave and protected only by `piix_lock`; wrong bit selection can corrupt sibling-device timings. SIDPR access is probed defensively because some systems expose registers that do not work. Suspend/resume has special handling for known broken Toshiba/Sony systems. Global mutation of `piix_port_info[ent->driver_data].flags` for broken poweroff systems can affect later probes of the same controller type. Hyper-V ignore policy intentionally suppresses ATA disks while keeping emulated optical devices.

## Test Signals
Coverage should include PIIX/ICH PATA timing mode transitions, 40/80-wire cable detection including laptop short-cable entries, ICH5/ICH6/ICH8 SATA map values, PCS enabling delays, SIDPR success/failure paths, VMware BMDMA status masking, 450NX errata detection, Clevo IOCFG restore, Hyper-V/Virtual PC DMI behavior, suspend/resume on broken and normal systems, and removal restoring IOCFG. Useful runtime traces are port map logs, DMA mask changes, SCR read/write behavior, and libata EH after reset or PMP errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ata_piix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libahci.c -->
# sources/distributed-fs/ceph-client/drivers/ata/libahci.c

## Purpose
`libahci.c` is the common AHCI SATA engine used by PCI, platform, and other AHCI host drivers. It owns AHCI capability normalization, controller reset/init, port DMA/FIS setup, command preparation and issue, interrupt handling, libata error recovery integration, power management, port multiplier/FBS support, enclosure-management LED support, and host activation.

## Important APIs, Types, And Functions
The primary exported operation table is `ahci_ops`, with `ahci_pmp_retry_srst_ops` as a soft-reset workaround variant. Exported helpers include `ahci_save_initial_config()`, `ahci_reset_controller()`, `ahci_init_controller()`, `ahci_dev_classify()`, `ahci_fill_cmd_slot()`, `ahci_kick_engine()`, `ahci_do_softreset()`, `ahci_check_ready()`, `ahci_do_hardreset()`, `ahci_qc_issue()`, `ahci_error_handler()`, `ahci_port_resume()`, `ahci_print_info()`, `ahci_set_em_messages()`, and `ahci_host_activate()`. The file exports sysfs attribute groups `ahci_shost_groups` and `ahci_sdev_groups`.

Key state is carried in `struct ahci_host_priv`, `struct ahci_port_priv`, `struct ahci_em_priv`, libata `ata_port`, `ata_link`, and `ata_queued_cmd`. Module parameters include `skip_host_reset`, `ignore_sss`, `ahci_em_messages`, and `devslp_idle_timeout`.

## Control Flow
Host setup starts with a caller-populated `ahci_host_priv`. `ahci_save_initial_config()` enables AHCI mode, reads CAP/CAP2/version/ports-implemented, applies platform/quirk overrides, fabricates legacy port maps when needed, saves per-port command capability bits, and installs default `start_engine`, `stop_engine`, and IRQ handler callbacks. `ahci_reset_controller()` performs a global reset unless skipped, reenables AHCI mode, and restores saved hardware-init fields when allowed. `ahci_init_controller()` deinitializes each real port, clears pending SError/IRQ state, and enables global host interrupts.

Port startup allocates coherent DMA memory for command slots, received FIS area, and command tables; detects FBS capability; optionally switches to per-port locks for multi-MSI; then resumes the port. Resume powers up/spins up the link, starts FIS reception, starts the DMA engine unless delayed, restores enclosure-management LEDs, initializes software activity timers, and attaches/detaches PMP/FBS state according to current topology.

For command execution, `ahci_qc_prep()` converts ATA taskfiles into command FISes, copies ATAPI CDBs, fills AHCI scatter/gather entries, and writes command slot options. `ahci_qc_issue()` records the active link, marks NCQ commands in `PORT_SCR_ACT`, selects the FBS PMP device when needed, writes `PORT_CMD_ISSUE`, and updates software activity. Completion reads `PORT_SCR_ACT` and/or `PORT_CMD_ISSUE` depending on FBS and NCQ state, then calls libata multi-completion and fills result taskfiles from D2H, PIO setup, or SDB FIS areas.

Reset and error handling paths stop/kick engines, issue software-reset FIS pairs with deadline handling, perform SATA hardreset after clearing D2H receive state, classify devices from `PORT_SIG`, set ATAPI command bits after reset, clear SError, map AHCI IRQ bits into libata error masks/actions, handle hotplug/PHY changes, abort/freeze ports, and delegate recovery to `sata_pmp_error_handler()`. Host IRQ handling supports both shared single-level interrupts and one-MSI-per-port mode.

## State And Persistence
`hpriv` stores normalized capabilities, saved hardware-init register values, port map, MMIO base, IRQ vectors, EM buffer metadata, and quirk flags. `pp` stores DMA pointers, interrupt mask, active link, FBS state, optional IRQ descriptions, and per-port EM state. Hardware state is in AHCI global registers, per-port command/interrupt/SCR/FBS/DEVSLP registers, DMA command lists, received FIS buffers, and EM buffers. Sysfs writes can persist runtime LED/activity choices in `ahci_em_priv` until port teardown.

## Dependencies And Integration Points
The file is the bridge between libata core and AHCI MMIO hardware. It depends on DMA mapping, runtime PM, SCSI host attributes, PCI/platform callers, SATA PMP helpers, libata EH, ACPI storage D3 checks, timer APIs, and AHCI register definitions from `ahci.h`. `libahci_platform.c` and PCI AHCI drivers call its exported reset/init/activate/resource-independent routines.

## Risks And Edge Cases
Many operations depend on strict ordering: engines must stop before CLO/DEVSLP/FBS changes, FIS RX must be programmed before command issue, HOST_IRQ_STAT must be cleared after port status, and SError must be cleared to avoid lockups. Hardware quirks can force 32-bit DMA, disable NCQ/PMP/SNTF/DEVSLP/FBS/SXS, or change ALPM behavior. Hot-unplug can make registers read `0xffffffff`. FBS changes result-FIS ownership and PMP error routing. Sysfs EM buffer access must reject busy or unsupported states. DEVSLP programming stops the engine and may fail device feature commands. Global host reset can be skipped by parameter, which avoids broken firmware but leaves stale state possible.

## Test Signals
Useful tests include AHCI capability normalization for quirk flags and firmware-supplied port maps, reset timeout/failure paths, DMA mask selection, port start/stop leaks, NCQ and non-NCQ completion, ATAPI CDB paths, PMP with and without FBS, BAD_PMP retry softreset, hotplug/PHYRDY interrupts, SNotification fallback, multi-MSI interrupt registration, runtime/system suspend with SSS and DEVSLP, EM LED and SGPIO sysfs operations, and EH recovery from TF, host-bus, interface, unknown-FIS, and command-timeout errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libahci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libahci_platform.c -->
# sources/distributed-fs/ceph-client/drivers/ata/libahci_platform.c

## Purpose
`libahci_platform.c` is the common platform-device resource and lifecycle layer for AHCI controllers that are not plain PCI AHCI devices. It discovers firmware-described MMIO, clocks, regulators, resets, PHYs, port child nodes, and platform capability overrides, sequences those resources safely, and then invokes `libahci.c` to initialize and activate the ATA host.

## Important APIs, Types, And Functions
The file exports `ahci_platform_ops`, which inherits `ahci_ops` and overrides `host_stop` so platform-managed resources are disabled on host teardown. Exported resource helpers include `ahci_platform_enable_phys()`, `ahci_platform_disable_phys()`, `ahci_platform_find_clk()`, `ahci_platform_enable_clks()`, `ahci_platform_disable_clks()`, `ahci_platform_deassert_rsts()`, `ahci_platform_assert_rsts()`, `ahci_platform_enable_regulators()`, `ahci_platform_disable_regulators()`, `ahci_platform_enable_resources()`, `ahci_platform_disable_resources()`, `ahci_platform_get_resources()`, `ahci_platform_init_host()`, `ahci_platform_shutdown()`, and PM helpers under `CONFIG_PM_SLEEP`.

Private helpers discover per-port PHYs/regulators, parse firmware properties (`hba-cap`, `ports-implemented`, `hba-port-cap`), find the maximum DT port id, and release manually acquired target regulators through a devres callback.

## Control Flow
`ahci_platform_get_resources()` opens a devres group, computes the number of ports from DT child `reg` values, allocates `ahci_host_priv` with room for PHY pointers, maps the AHCI MMIO resource, obtains clocks in bulk or falls back to one optional clock, obtains controller and PHY regulators, optionally obtains reset arrays, allocates non-devm target regulator storage, and walks child nodes. For each enabled child node it validates the port id, optionally creates/finds a child platform device to get the target regulator, gets the port PHY, and builds a mask of enabled ports. With no child nodes, it keeps compatibility by probing port 0 resources from the parent node. Firmware overrides are read, runtime PM is enabled and acquired, and the devres group is retained on success or released atomically on failure.

Resource enabling is ordered regulators, clocks, resets, PHYs; failures unwind in reverse. Disabling reverses that order. PHY enable initializes each non-ignored PHY, sets SATA mode, powers it on, and unwinds previously enabled PHYs if a later port fails. Regulator enable handles controller, PHY, and per-port target regulators with reverse-order cleanup.

`ahci_platform_init_host()` obtains IRQ 0, saves AHCI initial config, derives ATA flags for NCQ/PMP/EM, allocates an ATA host sized by CAP.NP and port map, configures parallel scan based on SSS, tags each port with MMIO descriptions, dummy-disables ports outside the implemented map, coerces 64-bit DMA if supported, resets and initializes the controller, prints AHCI info, and calls `ahci_host_activate()`. Shutdown freezes/stops each port and clears host interrupts to make kexec safe. Suspend/resume helpers disable/enable interrupts, host state, PHYs, resources, and runtime PM state in the expected order.

## State And Persistence
Runtime state is stored in `ahci_host_priv`: MMIO base, IRQ, clocks, regulators, resets, PHY pointers, target power regulators, firmware-supplied capability/port-map overrides, port masks, and a `got_runtime_pm` flag. Device-tree child nodes and regulator references drive per-port state. No durable state is written; hardware resources are enabled/disabled and AHCI register state is initialized by `libahci`.

## Dependencies And Integration Points
The file depends on platform devices, OF/device-tree APIs, clocks, regulators, reset controllers, generic PHY, runtime PM, DMA masks, libata, and `libahci.c` exported helpers. Board-specific AHCI platform drivers typically call `ahci_platform_get_resources()`, `ahci_platform_enable_resources()`, and `ahci_platform_init_host()` from probe and reuse the exported PM/shutdown helpers.

## Risks And Edge Cases
Resource ordering is safety-critical: PHYs should not power on before regulators/clocks/resets are ready, and error unwinds must not leave power rails active. Child-node port ids beyond allocated `nports` are warned and ignored; too many child nodes fail probe. Target regulators are not devm-managed because they belong to child devices, so the devres release callback must run. `pm_runtime_get_sync()` return is not explicitly checked, so platforms with runtime-PM failures need scrutiny. Firmware overrides can mask ports or capabilities incorrectly. Suspend with `AHCI_HFLAG_NO_SUSPEND` fails intentionally to avoid corrupt firmware behavior.

## Test Signals
Useful validation includes DTs with no child ports, sparse child port IDs, invalid IDs, disabled children, per-port regulators, missing optional clocks, deferred PHY/regulator probes, reset-trigger versus reset-assert semantics, resource-enable failure injection at each stage, 64-bit DMA coercion, dummy disabled ports, SSS parallel-scan behavior, kexec shutdown with interrupts cleared, system suspend/resume, and runtime PM state after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libahci_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/ata/libata-acpi.c

## Purpose
`libata-acpi.c` provides ACPI integration for libata PATA and SATA devices. It binds ATA ports/devices to ACPI namespace objects, handles ACPI dock/bay hotplug notifications, evaluates and applies ACPI timing/taskfile methods (`_GTM`, `_STM`, `_GTF`, `_SDD`), manages ACPI power states for ATA devices, and disables ACPI integration after repeated failures.

## Important APIs, Types, And Functions
The file exposes `ata_dev_acpi_handle()`, `ata_acpi_bind_port()`, `ata_acpi_bind_dev()`, `ata_acpi_dev_manage_restart()`, `ata_acpi_port_power_on()`, `ata_acpi_dissociate()`, `ata_acpi_gtm()`, `ata_acpi_stm()`, `ata_acpi_gtm_xfermask()`, `ata_acpi_cbl_pata_type()`, `ata_acpi_on_resume()`, `ata_acpi_set_state()`, `ata_acpi_on_devcfg()`, and `ata_acpi_on_disable()`. `struct ata_acpi_gtf` models seven ATA taskfile registers returned by `_GTF`; `struct ata_acpi_hotplug_context` attaches libata port/device pointers to ACPI hotplug callbacks.

The `acpi_gtf_filter` module parameter controls filtering of risky `_GTF` commands such as transfer-mode changes, lock/freeze commands, DIPM, and FPDMA feature toggles.

## Control Flow
Binding starts from ACPI companion devices. PATA ports preset a port companion from the host companion and port number; SATA devices preset device companions with `_ADR` values derived from host port and PMP number. Both port and device binding allocate ACPI hotplug contexts when the ACPI object exists and no hotplug context is already installed.

ACPI notifications flow into `ata_acpi_handle_hotplug()`. Bus/device checks mark the port hotplugged and freeze it for EH. Eject requests mark a specific device or all edge-link devices for detach, schedule EH, and wait for EH completion. Separate uevent callbacks emit `BAY_EVENT=<event>` on the SCSI device or ATA port kobject.

Timing support uses `_GTM` to capture BIOS timing values, `_STM` to restore them with IDENTIFY buffers for master/slave, and `_GTM`-derived masks to infer PATA cable type. `_GTF` is evaluated lazily and cached in `dev->gtf_cache`; returned seven-byte taskfiles are converted to `ata_taskfile`, filtered, and executed through `ata_exec_internal()`. SATA configuration also calls `_SDD` with byte-swapped IDENTIFY data before `_GTF`. After any executed `_GTF` command, IDENTIFY data is reread.

Resume restores initial `_GTM` timing through `_STM` where available, refreshes or schedules `_GTF`, and marks devices with `ATA_DFLAG_ACPI_PENDING`. Device configuration runs pending ACPI work, retries once on failures, then sets `ATA_DFLAG_ACPI_DISABLED` after a second failure. Power-state helpers select ACPI D states for SATA devices individually, handle runtime ATAPI/ZPODD D3-cold restrictions, and sequence PATA channel/device power according to ACPI requirements.

## State And Persistence
Runtime state is held in ACPI companion bindings on `ap->tdev` and `dev->tdev`, hotplug contexts allocated per ACPI object, `ap->__acpi_init_gtm`, `ATA_PFLAG_INIT_GTM_VALID`, `dev->gtf_cache`, and device flags such as `ATA_DFLAG_ACPI_PENDING`, `ATA_DFLAG_ACPI_FAILED`, `ATA_DFLAG_ACPI_DISABLED`, and `ATA_DFLAG_DETACH`. Hardware/firmware state is mutated through ACPI power resources, `_STM` timing settings, and ATA taskfile commands from `_GTF`.

## Dependencies And Integration Points
The file depends on ACPI core object evaluation, ACPI power management, ACPI hotplug contexts, libata EH and internal command execution, SCSI device objects for uevents, PCI/libata structures, runtime PM, and ZPODD helpers. It is called from libata probe, resume, device configuration, disable, detach, and power-management paths.

## Risks And Edge Cases
Firmware-provided `_GTF` commands can be harmful; filtering prevents transfer-mode conflicts and lock/security/FPDMA/DIPM surprises by default. `_GTF` cache ownership is manual and must be cleared on disable/resume/error. Partial ACPI failures are tolerated only when no taskfile executed and the port is not frozen; otherwise EH retries and may disable ACPI for the device. `_STM` depends on valid 512-byte IDENTIFY buffers for both device slots. SATA and PATA use different ACPI companion topology and power sequencing, so incorrect `ATA_FLAG_ACPI_SATA` use can target the wrong namespace object. Runtime D3-cold for ATAPI is restricted to ZPODD-ready devices.

## Test Signals
Useful tests include ACPI namespace binding for PATA ports, SATA devices, and PMP devices; dock/bay add/eject notifications; uevent generation; `_GTM` success, not-found, wrong-type, and wrong-length cases; `_STM` execution and restore on dissociate/resume; `_GTF` caching, filtering, command rejection, command failure, and retry-disable behavior; `_SDD` IDENTIFY byte-swapping; PATA cable inference from GTM; SATA/PATA suspend and resume power sequencing; and ZPODD runtime D3-cold behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-acpi.c -->
