# Research Group subset-b-005004

This grouped report covers PCIe controller sources under `sources/distributed-fs/ceph-client/drivers/pci/controller`. Each source section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-brcmstb.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-brcmstb.c

## Purpose

`pcie-brcmstb.c` is the Broadcom STB/Raspberry Pi style PCIe Root Complex platform driver. It brings a Broadcom controller from reset into RC mode, programs outbound and inbound address translation, starts the downstream link, optionally exposes an internal MSI parent domain, handles downstream device regulators, supports suspend/resume, and can dump controller outbound-error registers during die/panic notifiers on SoCs that advertise error reporting.

## Important APIs, Types, And Functions

- `struct brcm_pcie` is the main runtime state: MMIO base, optional clock, DT node, link generation limit, MSI target address, reset controls, RESCAL reset, memory-controller sizes, subdevice regulators, SoC config, bridge reset state, and notifier/lock state.
- `struct pcie_cfg_data` is the SoC descriptor. It selects register offsets, SoC family, PERST and bridge reset callbacks, inbound-window count, optional PHY handling, optional post-setup hook, and error-report support.
- `struct brcm_msi` owns internal MSI state: IRQ domains, bitmap allocator, target address, chained IRQ, legacy/non-legacy register layout, and interrupt register base.
- `brcm_pcie_probe()` allocates a `pci_host_bridge`, maps registers, gets clocks/resets, powers PHY/reset blocks, calls `brcm_pcie_setup()`, configures MSI, registers the host bridge, and optionally registers panic/die notifiers.
- `brcm_pcie_setup()` is the central hardware setup path. It resets the bridge, clears SerDes IDDQ, configures burst/read behavior, computes inbound windows from `dma-ranges`, programs outbound windows from host resources, sets RC class code, applies link capability overrides, and calls the SoC post-setup hook.
- `brcm_pcie_start_link()` deasserts PERST, waits for PHY/data-link active, configures CLKREQ/L1SS policy, optionally enables SSC through MDIO, and logs negotiated link speed/width.
- `brcm_pcie_map_bus()` and `brcm7425_pcie_map_bus()` provide config-space access using RC-local registers for bus 0 and indexed external config windows for downstream buses.
- `brcm_pcie_enable_msi()`, `brcm_allocate_domains()`, `brcm_pcie_msi_isr()`, and `brcm_msi_set_regs()` implement the MSI parent domain and hardware MSI registers.
- `brcm_pcie_suspend_noirq()` and `brcm_pcie_resume_noirq()` quiesce the link, power/reset blocks, regulators, clocks, and MSI registers across system sleep.
- `brcm_pcie_dump_err()` reads and clears outbound config/memory error registers under `bridge_lock` and reports decoded error data during panic/die notifications.

## Control Flow

Probe starts with `devm_pci_alloc_host_bridge()`, OF match data lookup, `devm_platform_ioremap_resource()`, optional `sw_pcie` clock, optional reset controls (`rescal`, `perst`, `bridge`, `swinit`), and `clk_prepare_enable()`. The bridge is deasserted early so registers are accessible, optional `swinit` is pulsed, RESCAL is reset, optional PHY is started, and `brcm_pcie_setup()` initializes controller translation and RC identity. After setup, hardware revision gates unsupported BCM4908 revisions. If MSI is enabled and the controller is its own `msi-parent`, the internal MSI domain is created. The `pci_host_bridge` receives Broadcom config ops and `pci_host_probe()` enumerates the bus; a post-probe link check rejects a link that dropped during scan.

Normal config access avoids CPU aborts by returning `NULL` for downstream config cycles when the link is down. RC config cycles use the controller register block directly. For downstream devices the driver writes an ECAM-derived index and returns the data window.

Power management shuts down in reverse: request L23 when linked, assert PERST, clear L23 request, set SerDes IDDQ, optionally assert bridge reset, stop PHY, rearm RESCAL, disable downstream regulators unless a child device can wake the system, and disable the clock. Resume re-enables the clock, resets RESCAL, starts PHY, deasserts bridge reset, reruns setup, re-enables regulators when needed, restarts the link, and restores MSI registers.

## State And Persistence

The driver persists only kernel runtime state and hardware register state. `bridge_in_reset` mirrors bridge reset state for panic-safe error dumping. `pcie->sr` stores downstream regulator handles acquired during `add_bus` and released during `remove_bus`. `ep_wakeup_capable` records a suspend-time decision to keep regulators enabled for wake-capable endpoints. MSI allocation is tracked in the `brcm_msi.used` bitmap under a mutex. Inbound memory-controller sizing is derived from `dma-ranges` and optional `brcm,scb-sizes` every setup/resume; outbound and inbound windows are reprogrammed on resume.

## Dependencies And Integration Points

The driver integrates with OF platform binding (`brcm,bcm2711-pcie`, `brcm,bcm2712-pcie`, `brcm,bcm4908-pcie`, `brcm,bcm7216-pcie`, and related compatibles), the PCI host bridge core, generic config accessors, reset and clock frameworks, regulator framework for downstream supplies, PHY/RESCAL reset controls, MSI irqdomain/`irq-msi-lib`, chained IRQ handling, panic/die notifier chains, and DT properties such as `dma-ranges`, `msi-parent`, `brcm,enable-ssc`, `brcm,clkreq-mode`, `aspm-no-l0s`, `num-lanes`, and `brcm,scb-sizes`.

## Risks And Edge Cases

- `brcm_pcie_get_inbound_wins()` has strict alignment and power-of-two assumptions. Bad or firmware-mutated `dma-ranges` can fail setup, and non-BCM7712 SoCs rely on inferred memory-controller size if `brcm,scb-sizes` is absent.
- Config-space access while link is down can cause CPU aborts, so link gating in `map_bus()` is a critical safety behavior.
- MSI target address selection depends on inbound window placement; devices requiring 32-bit MSI may fail if only the above-4G target is safe.
- CLKREQ/L1SS mode is DT-controlled and documented as capable of hanging traffic if misconfigured with an incompatible endpoint.
- Panic/die error dumping uses MMIO during exceptional paths and depends on `bridge_lock` plus `bridge_in_reset` to avoid accessing an off bridge.
- `CFG_QUIRK_AVOID_BRIDGE_SHUTDOWN` exists because some SoCs lose access to RESCAL or can hang fabric when a bridge is shut down.

## Test Signals

Useful validation includes successful platform probe, `pci_host_probe()` enumeration, expected "link up" speed/width logs, correct `lspci` bridge class, MSI allocation and interrupt delivery from endpoint devices, suspend/resume with and without wake-capable endpoints, regulator enable/disable behavior on root bus add/remove, DT variations for `dma-ranges`, `num-lanes`, `brcm,clkreq-mode`, and MSI parent, and injected link-down or bad-DT cases showing clean `-ENODEV`/`-EINVAL` failures rather than aborts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-brcmstb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-hisi-error.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-hisi-error.c

## Purpose

`pcie-hisi-error.c` is an ACPI/APEI GHES vendor-record handler for HiSilicon HIP PCIe controller errors. It recognizes a HiSilicon-specific CPER section GUID, decodes controller error payload fields, logs valid metadata and miscellaneous registers, and attempts recovery for recoverable errors by removing and rescanning the affected root port after invoking an ACPI reset method.

## Important APIs, Types, And Functions

- `struct hisi_pcie_error_data` models the vendor CPER payload: validity bitmap, topology identifiers, submodule, severity/type, and 33 miscellaneous registers.
- `struct hisi_pcie_error_private` stores the GHES notifier and owning device.
- `hisi_pcie_notify_error()` is the GHES notifier callback. It filters by section GUID and ACPI device `socket` property before handling the payload.
- `hisi_pcie_handle_error()` logs all valid fields and misc registers, then triggers recovery only when severity is `HISI_PCIE_ERR_SEV_RECOVERABLE`.
- `hisi_pcie_port_do_recovery()` locates the ACPI PCI root, gets the root port `pci_dev`, removes it under PCI locking, calls the reset method, waits one second, and rescans the root bus.
- `hisi_pcie_port_reset()` evaluates ACPI method `RST` with socket/chip, core ID, and core port ID arguments derived from firmware port identifiers.
- `hisi_pcie_error_handler_probe()` allocates private state and registers the vendor-record notifier with `devm_ghes_register_vendor_record_notifier()`.

## Control Flow

The platform driver binds via ACPI ID `HISI0361`. Probe allocates private notifier state and registers with GHES. On each vendor CPER notification, the callback imports the section GUID, ignores records for other vendors, verifies the platform device socket property, and ignores records for other sockets. Matching records are decoded and logged. For recoverable severity, the code computes the PCI root-port devfn from core/port IDs, removes the root port and downstream devices, calls ACPI `RST`, waits for subordinate device initialization time, and rescans the ACPI root bus.

## State And Persistence

There is almost no persistent driver state beyond the registered notifier and device pointer. Recovery intentionally changes PCI core state by hot-removing and rescanning devices under the affected root port. Error information is consumed from the GHES-provided buffer; it is not stored after logging. The ACPI firmware owns reset semantics and persistent platform topology.

## Dependencies And Integration Points

The driver depends on ACPI GHES vendor-record notification, `acpi_hest_get_payload()`, ACPI root lookup (`acpi_pci_find_root()`), PCI core hot-remove/rescan helpers, ACPI method `RST`, and a device property named `socket`. It integrates with platform-driver matching through ACPI table `HISI0361`.

## Risks And Edge Cases

- Payload validation is based on `val_bits`, but recovery still uses `socket_id`, `core_id`, and `port_id` fields for recoverable errors; malformed firmware records could target the wrong root port.
- `pci_stop_and_remove_bus_device_locked()` disrupts all downstream devices. Driver correctness depends on re-enumeration and endpoint driver recovery.
- The one-second wait is conservative but fixed; endpoints with unusual readiness behavior may still fail rescan.
- If ACPI `RST` is absent or returns failure, recovery stops after the root port was removed, leaving recovery to later rescans or manual intervention.
- The notifier ignores records without a matching `socket` property, so platform firmware and ACPI device properties must agree.

## Test Signals

Test by injecting or replaying GHES records with the HiSilicon GUID, verifying nonmatching GUIDs and sockets return `NOTIFY_DONE`, checking decoded log output for each valid bit, confirming recoverable errors remove and rescan only the targeted root port, testing missing/failing ACPI `RST`, and ensuring fatal/corrected/none severities log without hot-remove recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-hisi-error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-bcma.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-bcma.c

## Purpose

`pcie-iproc-bcma.c` is the BCMA bus wrapper for Broadcom iProc PCIe controllers. It adapts a BCMA core into the common `iproc_pcie` host-controller implementation by supplying MMIO base, physical base, a fixed 128 MiB memory window, an IRQ mapping callback, and BCMA driver registration.

## Important APIs, Types, And Functions

- `iproc_bcma_pcie_probe()` allocates the PCI host bridge, initializes `struct iproc_pcie`, creates the bridge memory resource from BCMA address data, requests bus resources, installs `map_irq`, stores driver data, and calls `iproc_pcie_setup()`.
- `iproc_bcma_pcie_map_irq()` maps PCI legacy IRQs to BCMA core IRQ line 5.
- `bcma_pcie2_fixup_class()` is an early PCI fixup for Broadcom device IDs `0x8011` and `0x8012`, forcing the class to normal PCI bridge because hardware reports the wrong class.
- `iproc_bcma_pcie_remove()` delegates teardown to `iproc_pcie_remove()`.

## Control Flow

When a BCMA core matching `BCMA_CORE_NS_PCIEG2` probes, the wrapper allocates host bridge private data, sets type `IPROC_PCIE_PAXB_BCMA`, uses `bdev->io_addr` and `bdev->addr` as controller register mappings, constructs a fixed memory resource from `addr_s[0]`, and calls the common core. From that point the common iProc file controls reset, link check, config access, MSI, and bus scanning.

## State And Persistence

The wrapper only persists the common `struct iproc_pcie` in BCMA driver data and the host bridge resource list. The fixed memory window is runtime kernel state and is released through devm/resource cleanup and common remove.

## Dependencies And Integration Points

It depends on the BCMA bus API, PCI host bridge allocation, `devm_request_pci_bus_resources()`, and the shared `pcie-iproc.h` interface. It has no OF parsing and no platform clocks/resets of its own.

## Risks And Edge Cases

- The memory aperture is hard-coded to 128 MiB from `bdev->addr_s[0]`; boards requiring a different aperture are not represented here.
- If `bdev->io_addr` is missing, probe fails with `-ENOMEM`.
- Legacy IRQ routing assumes BCMA IRQ line 5.
- The class fixup is device-ID-specific; unlisted BCMA variants with similar class bugs would remain misclassified.

## Test Signals

Expected signals are BCMA probe success, requested memory resource coverage, root bridge class fixed for IDs `0x8011/0x8012`, functional legacy INTx via BCMA IRQ 5, downstream enumeration through `iproc_pcie_setup()`, and clean common teardown on BCMA remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-bcma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-msi.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-msi.c

## Purpose

`pcie-iproc-msi.c` implements the internal event-queue MSI controller used by older Broadcom iProc PCIe variants when MSI is not handled by an external GIC ITS. It creates a PCI MSI parent domain, allocates MSI vectors across hardware event queues, programs event-queue and MSI write-address memory, chains GIC interrupts, and supports CPU-affinity steering by changing hardware IRQ numbers.

## Important APIs, Types, And Functions

- `struct iproc_msi` owns MSI controller state: register layout, GIC IRQ groups, CPU count, vector bitmap, IRQ domain, DMA event queue memory, and MSI posted-write address.
- `struct iproc_msi_grp` binds one GIC interrupt to one MSI event queue.
- `iproc_msi_init()` validates the MSI OF node, sizes IRQ groups, selects PAXB/PAXC register layouts, allocates vector bitmap and group state, maps GIC IRQs, allocates coherent event queue memory, creates the parent MSI domain, installs chained handlers for online CPUs, and enables hardware.
- `iproc_msi_exit()` disables hardware, removes chained handlers, removes the IRQ domain, frees coherent memory, and disposes IRQ mappings.
- `iproc_msi_handler()` drains an event queue by comparing head/tail pointers, decodes MSI data, dispatches through `generic_handle_domain_irq()`, and advances the head pointer.
- `iproc_msi_irq_domain_alloc()` and `iproc_msi_irq_domain_free()` manage vector allocation with CPU-stride reservations.
- `iproc_msi_irq_set_affinity()` rewrites `irq_data->hwirq` to select the target CPU's group.
- `iproc_msi_irq_compose_msi_msg()` writes the MSI target address and data payload expected by iProc hardware.

## Control Flow

The common iProc host code calls `iproc_msi_init()` when an `msi-parent` or `msi-map` node is compatible with `brcm,iproc-msi`. Initialization rejects nodes without `msi-controller`, existing MSI state, insufficient GIC IRQs for CPU affinity, and incompatible controller types. It may reduce the IRQ group count to a multiple of CPU count. After allocating state, it maps each GIC IRQ, allocates DMA memory for event queues, creates the MSI parent domain, installs chained handlers per online CPU, programs queue pages and MSI address pages, and enables queue interrupts. Runtime MSI delivery enters through the chained GIC IRQ, drains queue entries, decodes canonical hardware IRQs, and dispatches to the inner domain.

## State And Persistence

MSI vector ownership persists in `msi->bitmap` under `bitmap_lock`. Event queue contents live in coherent DMA memory shared with hardware. `irq_data->hwirq` can change when affinity changes; canonical hardware IRQ allocation remains CPU0-based for freeing. Register state is programmed during enable and cleared during disable. The file does not write persistent storage.

## Dependencies And Integration Points

The file depends on OF MSI nodes, `of_irq_count()`, `irq_of_parse_and_map()`, irqdomain MSI library, chained IRQ APIs, coherent DMA allocation, CPU masks/online CPU iteration, and the shared `struct iproc_pcie`. It is compiled only when `CONFIG_PCIE_IPROC_MSI` exposes the declarations in `pcie-iproc.h`.

## Risks And Edge Cases

- MSI affinity assumes the number of hardware IRQ groups is at least the CPU count and is reduced to a multiple of CPUs. Hotplug or unusual CPU topology could leave only online CPUs configured at init time.
- Multi-MSI allocation is rejected when multiple CPUs are present, because affinity steering reserves CPU-strided vectors.
- `CFG`/event queue memory ordering depends on hardware guarantee that queue data is visible before tail update.
- `iproc_msi_exit()` does not explicitly set `pcie->msi = NULL`; teardown order currently prevents reuse, but reinitialization assumptions should be checked if lifecycle changes.
- The parent ops object is global and has supported flags modified when `nr_cpus == 1`, so flag state is shared across instances.

## Test Signals

Validate with a `brcm,iproc-msi` node, multiple GIC IRQ counts, single-CPU and multi-CPU configurations, MSI and MSI-X endpoint interrupts, affinity changes, vector exhaustion, event queue wraparound, missing `msi-controller`, incompatible PAXB_V2/PAXC_V2 cases, teardown during remove, and `/proc/interrupts` distribution across expected GIC IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-platform.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-platform.c

## Purpose

`pcie-iproc-platform.c` is the OF platform wrapper for Broadcom iProc PCIe controllers. It maps controller registers, reads DT properties that select outbound/inbound mapping behavior and PHYs, chooses the iProc wrapper type from compatible data, and delegates host setup, remove, and shutdown to the shared iProc core.

## Important APIs, Types, And Functions

- `iproc_pcie_of_match_table` maps `brcm,iproc-pcie`, `brcm,iproc-pcie-paxb-v2`, `brcm,iproc-pcie-paxc`, and `brcm,iproc-pcie-paxc-v2` to `enum iproc_pcie_type`.
- `iproc_pltfm_pcie_probe()` allocates host bridge private state, maps resource 0 with `devm_pci_remap_cfgspace()`, reads optional outbound mapping properties, detects inbound mapping via `dma-ranges`, gets optional PHY, disables legacy IRQ mapping for PAXC types, and calls `iproc_pcie_setup()`.
- `iproc_pltfm_pcie_remove()` and `iproc_pltfm_pcie_shutdown()` delegate to `iproc_pcie_remove()` and `iproc_pcie_shutdown()`.

## Control Flow

Probe selects the controller type from OF match data, converts address resource 0 to a resource, maps it as config/MMIO space, and stores the physical base. If `brcm,pcie-ob` is present, `brcm,pcie-ob-axi-offset` becomes mandatory and `need_ob_cfg` is set. Presence of `dma-ranges` requests inbound mapping setup in the core. Optional PHY acquisition is performed before setup. PAXC controllers clear `map_irq` because they do not support legacy INTx. The common core then performs revision-specific setup, mapping, link checks, MSI handling, and host probing.

## State And Persistence

The wrapper stores all runtime state in `struct iproc_pcie` allocated as host bridge private data. DT-derived flags (`need_ob_cfg`, `need_ib_cfg`, `ob.axi_offset`, `type`, `phy`) persist for the common setup path. No persistent storage is used.

## Dependencies And Integration Points

This file depends on OF address parsing, OF PCI properties, PHY framework, platform resources, `devm_pci_alloc_host_bridge()`, `devm_pci_remap_cfgspace()`, and the exported functions from `pcie-iproc.c`. It relies on `pcie-iproc.h` for the shared state contract.

## Risks And Edge Cases

- `brcm,pcie-ob` without `brcm,pcie-ob-axi-offset` is a hard probe failure.
- The inbound mapping decision is a boolean based on `dma-ranges`; malformed ranges fail later in common mapping.
- `of_match_ptr()` around the match table means non-OF builds need care, though this driver is OF-oriented.
- PAXC disables only legacy IRQ mapping at this wrapper level; MSI steering and PAXC quirks are handled later and must remain consistent with selected type.

## Test Signals

Exercise each compatible string, with and without `brcm,pcie-ob`, missing `brcm,pcie-ob-axi-offset`, valid and invalid `dma-ranges`, optional PHY probe deferral, PAXC legacy IRQ absence, shutdown PERST assertion, and successful downstream enumeration through `iproc_pcie_setup()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc.c

## Purpose

`pcie-iproc.c` is the common Broadcom iProc PCIe host-controller implementation used by BCMA and platform wrappers. It abstracts PAXB/PAXC register layouts, configuration-space access, reset/link bring-up, outbound and inbound address translation, MSI steering to GIC ITS or internal MSI, PHY lifecycle, controller quirks, and PCI host registration.

## Important APIs, Types, And Functions

- `enum iproc_pcie_reg` and per-type register tables define valid offsets for PAXB BCMA, PAXB, PAXB v2, PAXC, and PAXC v2.
- `iproc_pcie_rev_init()` selects register tables and capabilities based on `pcie->type`, including config-read quirks, APB error disable, outbound/inbound map tables, internal endpoint behavior, and MSI steering.
- `iproc_pcie_config_read32()` and `iproc_pcie_config_write32()` wrap generic config access with optional APB error suppression and custom iProc reads.
- `iproc_pcie_config_read()` handles PAXB/PAXC custom reads, RRS retry status, PAXC capability fixups, and rejection of unconfigured physical functions.
- `iproc_pcie_check_link()` validates PHY/data-link status, verifies RC bridge mode, fixes class code, and retries Gen1 if a Gen2 link does not become active.
- `iproc_pcie_setup_ob()`, `iproc_pcie_map_ranges()`, `iproc_pcie_setup_ib()`, and `iproc_pcie_map_dma_ranges()` program outbound OARR/OMAP and inbound IARR/IMAP windows.
- `iproc_pcie_msi_enable()` resolves MSI nodes, performs optional MSI steering, and calls `iproc_msi_init()` for internal MSI when applicable.
- `iproc_pcie_setup()` is the exported setup entry point used by wrappers. It initializes revision state, PHY, PERST, address mappings, link, INTx, MSI, host bridge ops, scans the bus, and prints link status.
- `iproc_pcie_remove()` and `iproc_pcie_shutdown()` are exported lifecycle functions.

## Control Flow

Setup begins by selecting the register map and quirks. The PHY is initialized and powered, PERST is asserted and deasserted unless the endpoint is internal, and stale address mappings are invalidated. Optional outbound mappings are programmed from host bridge windows; optional inbound mappings are programmed from `dma_ranges`. Link checks are skipped for internal PAXC endpoints but otherwise verify hardware link bits and RC mode, force bridge class code, and possibly downshift to Gen1. The driver enables INTx, attempts MSI setup when `CONFIG_PCI_MSI` is enabled, installs `iproc_pcie_ops` on the host bridge, and scans. Remove stops and removes the root bus, disables MSI, powers off PHY, and exits PHY.

Config access uses an indirect address/data pair for RC config and endpoint config. For PAXB v2 reads, `iproc_pcie_cfg_retry()` handles hardware returning `0xffff0001` for RRS completions by polling config-read status. PAXC capability-list fixups alter returned config data for corrupted capability lists and hide unsupported RRS visibility.

## State And Persistence

`struct iproc_pcie` persists selected register offsets, mapping requirements, flags, and MSI pointer. Outbound/inbound mapping register state is invalidated and rebuilt at setup. `fix_paxc_cap` is latched after reading a known-bad device ID. MSI steering config persists in hardware until disabled or reset. No file-system persistence is used.

## Dependencies And Integration Points

The file integrates with PCI host bridge APIs, generic ECAM/config helpers, PHY framework, OF MSI translation, GICv3 ITS register definitions, irq/MSI support through `pcie-iproc-msi.c`, PCI fixup hooks, and wrapper-provided resources from BCMA or platform drivers. It exports setup/remove/shutdown symbols used by `pcie-iproc-bcma.c` and `pcie-iproc-platform.c`.

## Risks And Edge Cases

- `iproc_pcie_cfg_retry()` documents an ambiguity where real config data equal to `0xffff0001` can be mistaken for RRS retry status.
- Outbound mapping requires alignment and sufficient window sizes; the fallback minimum-window case can map more than the original resource.
- Inbound mapping must exactly match supported region sizes and alignments; malformed `dma-ranges` fail setup.
- PAXC unconfigured PF rejection relies on stale device ID `0x168e`; different firmware artifacts may escape rejection.
- MSI steering only supports GICv3 ITS and has separate PAXB v2 and PAXC v2 programming paths.
- Internal endpoints skip link and PERST handling, so behavior depends heavily on firmware pre-initialization.

## Test Signals

Run probe through both wrappers for every `iproc_pcie_type`, enumerate downstream devices, validate bridge class and link status, test RRS config retry and reads of `0xffff0001`, verify outbound/inbound mapping with aligned and unaligned resources, exercise internal PAXC PF rejection, check GIC ITS MSI steering and internal MSI fallback, test removal/shutdown PERST behavior, and verify PCI fixups for listed Broadcom device IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc.h

## Purpose

`pcie-iproc.h` defines the shared contract between Broadcom iProc PCIe wrappers, the common host-controller core, and the optional internal MSI implementation. It exposes controller type enumeration, mapping descriptors, the main `struct iproc_pcie`, and setup/remove/shutdown/MSI entry points.

## Important APIs, Types, And Functions

- `enum iproc_pcie_type` distinguishes BCMA PAXB, platform PAXB, PAXB v2, PAXC, and PAXC v2 wrappers.
- `struct iproc_pcie_ob` describes outbound mapping requirements: AXI offset and supported window count.
- `struct iproc_pcie_ib` describes inbound mapping region count.
- `struct iproc_pcie` is the shared mutable state for wrappers and core logic: device, type, register offsets, MMIO base, physical base, memory resource, optional PHY, IRQ mapping callback, endpoint/config quirks, outbound/inbound mapping state, MSI steering flag, and MSI pointer.
- `iproc_pcie_setup()`, `iproc_pcie_remove()`, and `iproc_pcie_shutdown()` are the common host lifecycle entry points.
- `iproc_msi_init()` and `iproc_msi_exit()` are declared when `CONFIG_PCIE_IPROC_MSI` is enabled and stubbed to `-ENODEV`/no-op otherwise.

## Control Flow

Wrappers allocate `struct iproc_pcie` as PCI host bridge private data, fill fields such as `dev`, `type`, `base`, `base_addr`, resources, optional PHY, and mapping flags, then call `iproc_pcie_setup()`. The common core fills `reg_offsets`, mapping tables, and runtime flags. MSI setup calls the header-provided `iproc_msi_init()` symbol, which either links to the MSI implementation or returns `-ENODEV` when the internal MSI driver is not configured.

## State And Persistence

The header itself has no state, but it defines which state is shared across files. The most important persistent fields are `reg_offsets`, `base/base_addr`, mapping flags/tables, quirk booleans, and `msi`. These fields remain valid from setup until remove/shutdown.

## Dependencies And Integration Points

It depends on kernel declarations for `struct device`, `struct resource`, `struct phy`, `struct pci_dev`, `struct list_head`, and device tree nodes through included users. It is included by `pcie-iproc.c`, `pcie-iproc-msi.c`, `pcie-iproc-platform.c`, and `pcie-iproc-bcma.c`.

## Risks And Edge Cases

- Many fields are initialized by wrappers and later assumed valid by the common core; missing `base`, wrong `type`, or inconsistent mapping flags cause setup failures or invalid MMIO.
- The MSI stubs mean callers must treat `-ENODEV` as an acceptable "not using internal MSI" outcome.
- Boolean quirk fields encode hardware behavior tightly; adding a new SoC requires careful field initialization in `iproc_pcie_rev_init()` and wrappers.

## Test Signals

Compile coverage with `CONFIG_PCIE_IPROC_MSI=y` and disabled, wrapper builds for BCMA and OF platform paths, setup calls with each enum value, static analysis for uninitialized shared fields, and runtime probe verifying wrappers populate the fields consumed by common setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-mediatek-gen3.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-mediatek-gen3.c

## Purpose

`pcie-mediatek-gen3.c` is the MediaTek/Airoha Gen3 PCIe Root Complex platform driver for newer single-controller hardware such as MT8192, MT8196, and EN7581. It powers and resets the controller/PHY, programs RC mode, link speed/width, address translation windows, INTx and MSI domains, downstream power-control devices, host bridge config access, and noirq suspend/resume.

## Important APIs, Types, And Functions

- `struct mtk_gen3_pcie` stores controller state: MMIO/physical base, resets, PHY, clocks, link parameters, IRQ domains, MSI sets, bitmaps, saved IRQ state, and SoC data.
- `struct mtk_gen3_pcie_pdata` supplies SoC-specific `power_up` callback, PHY reset names, optional system-clock-ready timing, and flags such as `SKIP_PCIE_RSTB`.
- `mtk_pcie_parse_port()` maps `pcie-mac`, gets reset controls, optional PHY, all clocks, and optional `num-lanes`.
- `mtk_pcie_power_up()` handles generic MT819x reset/PHY/clock/runtime-PM sequencing; `mtk_pcie_en7581_power_up()` handles Airoha EN7581-specific PBus setup, reset ordering, EQ presets, and clock-reset workaround.
- `mtk_pcie_startup_port()` sets RC mode, link speed/width, class code, INTx masking, DVFSRC behavior, MSI capture registers, ATR translation tables, downstream power, and link polling.
- `mtk_pcie_set_trans_table()` splits host bridge IO/MEM windows into up to eight power-of-two ATR windows.
- `mtk_pcie_init_irq_domains()`, `mtk_pcie_irq_handler()`, `mtk_pcie_msi_handler()`, and INTx/MSI chip/domain callbacks implement legacy and MSI interrupt delivery.
- `mtk_pcie_probe()` wires pwrctrl creation, IRQ setup, hardware setup, and `pci_host_probe()`.
- `mtk_pcie_suspend_noirq()` and `mtk_pcie_resume_noirq()` move the link to L2, save/restore IRQ registers, power down/up, and restart the port.

## Control Flow

Probe allocates a host bridge, stores SoC match data, creates IRQ domains/chained handler, creates PCI power-control devices, then parses and powers the controller. Setup parses resources before touching hardware, deasserts shared PHY resets to balance counts, calls the SoC power-up callback, optionally restricts max link speed from DT if the controller supports it, and starts the port. Startup programs controller capability and translation, powers endpoints, waits for link-up, and reports the LTSSM state on timeout. After successful setup, host bridge ops are installed and PCI scanning begins.

Interrupt flow enters a chained handler on the controller IRQ. INTx status bits are forwarded through a linear INTx domain using fasteoi semantics. MSI status bits select one of eight MSI sets; each set loops over enabled status bits and dispatches through the MSI bottom domain. MSI allocation uses a bitmap over 256 vectors and associates each vector with its owning `mtk_msi_set`.

## State And Persistence

The driver persists MSI vector allocation in `msi_irq_in_use`, saved top-level and per-set MSI enable registers across suspend, downstream power-control device state, and SoC-specific reset/clock state. Hardware ATR, MSI, INTx, and link registers are reprogrammed after power-up/resume. No disk persistence exists.

## Dependencies And Integration Points

It integrates with OF platform matching, PCI host bridge APIs, PCI pwrctrl, runtime PM, bulk clocks, reset controls, PHY framework, syscon/regmap for EN7581 PBus CSR, irqdomain/MSI parent library, chained IRQ handling, and DT properties/resources including `pcie-mac`, `num-lanes`, `max-link-speed`, `mediatek,pbus-csr`, `interrupt-controller`, and compatible-specific reset names.

## Risks And Edge Cases

- ATR translation has only eight entries and warns if resources exceed table capacity; unreachable resource tails may break endpoints.
- `mtk_pcie_probe()` has a `goto err_tear_down_irq; dev_err_probe(...)` ordering that makes the error log unreachable after pwrctrl creation failure.
- Link failure after endpoint power-up must unwind both endpoint power and controller power; EN7581 has a distinct reset path because normal PERST toggling is unsafe.
- MSI allocation uses contiguous bitmap regions and must keep set selection consistent for multi-MSI allocations.
- Suspend requires link transition to L2; failure aborts suspend.
- Invalid `num-lanes` is only warned and defaults to hardware behavior, which may hide DT mistakes.

## Test Signals

Validate probe on each compatible, pwrctrl creation/defer paths, EN7581 PBus programming, ATR programming for IO/MEM windows, max-link-speed and `num-lanes` DT handling, link timeout LTSSM logging, INTx and MSI interrupts across all sets, MSI masking/unmasking/ack, suspend/resume IRQ state restoration, endpoint power sequencing, and removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-mediatek-gen3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-mediatek.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-mediatek.c

## Purpose

`pcie-mediatek.c` is the older MediaTek/Airoha PCIe host driver for multi-port and Gen1/Gen2-era controllers including MT2701, MT7623, MT2712, MT7622, MT7629, and AN7583. It parses per-port DT nodes, powers clocks/PHYs, handles v1 and v2 config transaction mechanisms, sets up per-port INTx/MSI domains where supported, starts each link, registers one PCI host bridge, and manages suspend/resume.

## Important APIs, Types, And Functions

- `struct mtk_pcie` is top-level host state: shared base or syscon config, free clock, port list, and SoC descriptor.
- `struct mtk_pcie_port` stores per-port MMIO, clocks, reset, PHY, slot, IRQ domains, MSI bitmap, and controller backpointer.
- `struct mtk_pcie_soc` selects config ops, startup callback, IRQ setup callback, device ID fixup, and quirks.
- `mtk_pcie_parse_port()` maps a named `portN` resource, gets per-port clocks/resets/PHY, initializes IRQ domains, and links the port into the host list.
- `mtk_pcie_subsys_powerup()` maps optional `subsys`, gets optional generic syscon config, enables runtime PM and free clock.
- `mtk_pcie_enable_port()` powers per-port clocks/PHY, toggles reset, calls SoC startup, and removes the port from the active list if the link is down.
- `mtk_pcie_startup_port()` handles v1 reset/link, BAR0 DDR mapping, bridge class, FC credit, and FTS tuning.
- `mtk_pcie_startup_port_v2()` handles v2 LTSSM/ASPM enable, reset bits, ID/class quirks, link polling, INTx/MSI unmasking, and AHB/AXI translation.
- `mtk_pcie_startup_port_an7583()` adds Airoha PBus CSR setup before v2 startup.
- `mtk_pcie_config_read()`/`write()` plus `mtk_pcie_hw_rd_cfg()`/`wr_cfg()` implement v2 TLP-based config access. `mtk_pcie_map_bus()` implements v1 address/data config access.
- `mtk_pcie_intr_handler()` dispatches INTx and MSI from per-port chained IRQs.

## Control Flow

Probe allocates host bridge private state, selects SoC data, initializes the port list, parses either child nodes or a single-domain node, powers the shared subsystem, and attempts to enable each parsed port. Ports that fail link startup are logged and freed, leaving only active ports in the list. If every port disappears, the subsystem is powered down and the host bridge still probes with an empty port set. Host bridge ops are selected from the SoC descriptor; for v2 controllers config cycles are generated by writing TLP header registers and polling `APP_CFG_REQ` completion.

Interrupt setup creates a four-entry INTx domain per port and, when MSI is enabled and supported, a 32-vector MSI parent domain per port. The chained handler clears INTx status before dispatch and clears the top-level MSI status before draining individual MSI bits to avoid losing edge-triggered events.

Suspend disables per-port clocks and PHYs plus the free clock. Resume reenables the free clock and re-runs per-port enable/startup, which may remove ports if endpoints disappeared while suspended.

## State And Persistence

The active port list is mutable: failed or disconnected ports are removed and freed. Per-port MSI allocation persists in `msi_irq_in_use` under a mutex. Shared runtime PM and clock state persists while ports are active. Hardware class/device ID and translation windows are programmed during startup and restored by resume startup. There is no persistent storage.

## Dependencies And Integration Points

The driver depends on OF child node parsing, `of_pci_get_devfn()`, named platform resources/clocks/resets/PHYs, optional syscon `mediatek,generic-pciecfg`, Airoha `mediatek,pbus-csr`, runtime PM, PCI host bridge APIs, irqdomain and MSI libraries, and compatible-specific SoC descriptors.

## Risks And Edge Cases

- `mtk_pcie_enable_port()` frees a port on link-down during setup/resume; callers must tolerate the list shrinking.
- V2 config access reports `PCIBIOS_SET_FAILED` on completion timeout or completion status, which can affect enumeration diagnostics.
- MSI is per-port and limited to 32 vectors; multi-vector MSI is not supported by allocation (`WARN_ON(nr_irqs != 1)`).
- For v1, `host->msi_domain` is assigned a boolean expression for `MTK_PCIE_NO_MSI`, which is unusual and should be checked against PCI core expectations in this kernel tree.
- Reset and ID/class quirks are SoC-specific; a wrong compatible can leave bridge identity or reset sequencing broken.
- AN7583/EN-style PBus size masks depend on a power-of-two resource size.

## Test Signals

Test each compatible path, multi-child and single-domain DT layouts, link-up and link-down ports, v1 address/data config access, v2 TLP config completion failures, INTx dispatch, MSI allocate/ack/free, MT7622/MT7629 class/device quirks, AN7583 PBus CSR programming, suspend/resume with endpoint removal, and cleanup after `pci_host_probe()` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-mediatek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-mt7621.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-mt7621.c

## Purpose

`pcie-mt7621.c` is a built-in MediaTek/Ralink MT7621 PCIe host controller driver for up to three virtual PCIe bridges. It parses per-port resources from DT, handles MT7621 reset polarity quirks, powers PHYs and clocks, detects which slots have link, programs bridge windows and class codes, and registers a PCI host bridge using Type 1 style config access.

## Important APIs, Types, And Functions

- `struct mt7621_pcie` stores shared MMIO base, device pointer, active port list, and whether reset controls are inverted for MT7621 E2.
- `struct mt7621_pcie_port` stores per-port MMIO base, clock, PHY, reset control, optional GPIO endpoint reset, slot number, and enabled state.
- `mt7621_pcie_parse_dt()` maps shared registers and parses available child nodes with `of_pci_get_devfn()`.
- `mt7621_pcie_parse_port()` maps per-slot resources, gets child clock, reset, PHY, optional GPIO reset, and appends the port.
- `mt7621_pcie_init_ports()` asserts RC and EP resets, deasserts RC resets, initializes PHYs for ports except the special slot 1 path, deasserts EP resets, checks link status, disables empty ports, and handles shared PHY behavior between slots 0 and 1.
- `mt7621_pcie_enable_ports()` programs MEM/IO base registers, enables clocks for linked ports, enables per-port interrupts, maps BAR0 to DDR, fixes class/revision, and tunes FTS.
- `mt7621_pcie_map_bus()` programs `RALINK_PCI_CONFIG_ADDR` and returns the config data window for generic config access.
- `mt7621_pcie_probe()` handles host bridge allocation, SoC revision quirk detection, DT parse, port init, enable, and `pci_host_probe()`.

## Control Flow

Probe requires an OF node, allocates host bridge private state, initializes the port list, checks `soc_device_match()` for MT7621 E2 inverted resets, parses shared/per-port DT state, initializes ports and link status, enables active ports, and registers the host bridge. If no links are detected, it logs the condition and returns success without registering a host, treating an empty board as nonfatal.

Config cycles use `PCI_CONF1_EXT_ADDRESS()` written to a shared address register, with generic PCI config helpers reading/writing the data register. Startup programming uses helper `read_config()`/`write_config()` for RC-side tuning registers.

## State And Persistence

The port list persists for the driver lifetime. `enabled` records link-detected ports. Reset polarity is persisted in `resets_inverted`. Per-port PHY and clock state remains active for enabled ports; empty ports are reset/disabled. There is no persistent storage.

## Dependencies And Integration Points

The driver depends on OF child nodes and resources, child clocks, reset controls, GPIO descriptors for endpoint resets, PHY framework, `soc_device_match()` revision data, PCI host bridge APIs, and generic config access. It is registered with `builtin_platform_driver()` for `mediatek,mt7621-pci`.

## Risks And Edge Cases

- Slot 1 is treated specially during PHY init, and slot 0/1 share behavior can power off slot 0 PHY when both are disabled; board-specific topology matters.
- Reset polarity is tied to SoC revision match `mt7621` `E2`; missing revision data can invert reset behavior.
- `mt7621_pcie_probe()` returns success when no cards are connected, so absence of a PCI host may be expected but can surprise generic tests.
- Remove only releases reset controls; as a built-in legacy driver it does not perform full root bus teardown in its remove callback.
- IO resource is mandatory in `mt7621_pcie_enable_ports()`.

## Test Signals

Validate MT7621 E2 and non-E2 reset polarity, DT child parsing for all three ports, no-card boot returning success, linked slot enumeration, GPIO PERST timing, IO/MEM base programming, class code/FTS setup, generic config reads/writes, and clock enable failures unwinding reset controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-mt7621.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar-ep.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar-ep.c

## Purpose

`pcie-rcar-ep.c` is the Renesas R-Car PCIe endpoint-controller driver. It configures an R-Car PCIe block in endpoint mode, exposes PCI EPC operations to endpoint-function drivers, manages inbound BAR windows and outbound host-memory windows, programs endpoint headers/MSI capability, raises INTx/MSI interrupts, and initializes endpoint memory windows from platform resources.

## Important APIs, Types, And Functions

- `struct rcar_pcie_endpoint` wraps shared `struct rcar_pcie` with outbound memory window metadata, mapped outbound addresses, max functions, BAR-to-ATU mapping, inbound window bitmap, and window counts.
- `rcar_pcie_ep_hw_init()` places hardware in endpoint mode, initializes PCIe capabilities, header type, MPSS/MRRS, target speed, completion timeout, and capability termination.
- `rcar_pcie_ep_get_pdata()` maps controller registers, allocates outbound window descriptors, parses outbound memory resources, and reads `max-functions`.
- `rcar_pcie_parse_outbound_ranges()` collects `memoryN` platform resources into `pci_epc_mem_window` entries and requests those regions.
- `rcar_pcie_ep_write_header()` writes vendor/device/class/subsystem IDs and INTx pin into endpoint config registers.
- `rcar_pcie_ep_set_bar()` allocates inbound windows, rounds/alignment-limits BAR size, programs inbound translation, and waits for PHY readiness.
- `rcar_pcie_ep_map_addr()` finds the outbound window matching an EPC memory allocation, checks data link, and programs outbound translation to host PCI address.
- `rcar_pcie_ep_raise_irq()`, `rcar_pcie_ep_assert_intx()`, and `rcar_pcie_ep_assert_msi()` implement EPC interrupt requests.
- `rcar_pcie_ep_probe()` enables runtime PM, maps resources, allocates bitmaps, creates the EPC, initializes hardware and EPC memory windows, and calls `pci_epc_init_notify()`.

## Control Flow

Probe allocates endpoint state, resumes the device with runtime PM, gathers MMIO and outbound memory resources, allocates the inbound bitmap and outbound mapped-address table, creates a devm EPC using `rcar_pcie_epc_ops`, stores driver data, initializes endpoint hardware registers, initializes EPC memory windows with `pci_epc_multi_mem_init()`, and notifies endpoint-function drivers that the controller is ready.

Endpoint-function operations then call into this file. Header writes update config identity registers. BAR setup finds free inbound windows, marks a pair because BARs are treated as 64-bit, calculates the largest supported aligned size, and calls shared R-Car inbound programming. Outbound mapping requires the link to be up and uses the memory window whose physical base matches the EPC allocation. Start writes MAC and controller init bits; stop clears the controller enable register.

## State And Persistence

Inbound window allocation persists in `ib_window_map`; `bar_to_atu` remembers which inbound ATU index backs each BAR; `ob_mapped_addr` records outbound windows currently mapped to endpoint physical addresses. Hardware config registers persist until stop/reset/power loss. Runtime PM keeps the controller powered after probe. No disk persistence exists.

## Dependencies And Integration Points

The file depends on the shared R-Car PCIe helpers in `pcie-rcar.h`, the PCI endpoint controller framework (`pci_epc`, `pci_epc_mem_window`, endpoint-function callbacks), platform named memory resources (`memory0` and onward), OF address mapping, runtime PM, and Renesas compatible strings `renesas,r8a774c0-pcie-ep` and `renesas,rcar-gen3-pcie-ep`.

## Risks And Edge Cases

- `rcar_pcie_ep_get_pdata()` calls `rcar_pcie_parse_outbound_ranges()` but does not check its return value, so missing outbound resources may not abort as intended.
- `rcar_pcie_ep_clear_bar()` computes `atu_index` but calls `rcar_pcie_set_inbound()` with `bar` rather than the mapped ATU index, which looks suspicious when BAR numbers and inbound indices diverge.
- BAR setup marks `idx` and `idx + 1` without explicitly checking that `idx + 1` is within the bitmap.
- Outbound mapping matches only exact physical window bases; suballocations are intentionally not supported because page size equals window size.
- INTx is rejected when MSI is enabled or INTx disable is set; endpoint-function drivers need to select the right interrupt mode.

## Test Signals

Test probe with complete and missing `memoryN` resources, EPC creation, endpoint function binding, config header writes, BAR0/2/4 setup and clear, inbound bitmap exhaustion, outbound map/unmap before and after link-up, INTx and MSI interrupt generation, runtime PM failures, max-functions clamping, and host-side enumeration of the endpoint capabilities and BAR sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar-ep.c -->
