# sources/distributed-fs/ceph-client/drivers/scsi/advansys.c lines 8606-11554

## Scope

This chunk covers the final hardware-configuration and driver-registration portion of the AdvanSys SCSI adapter driver. It starts near the end of narrow-board `ASC_DVC_VAR` default initialization, then implements narrow-board EEPROM access and recovery, wide-board EEPROM defaults/read/write/init mapping, the `scsi_host_template`, wide-board DMA memory setup, common board discovery, resource registration, SCSI host registration, adapter release, VLB/EISA/PCI bus probe and remove paths, and module init/exit.

The chunk is not standalone. It relies on the command execution, interrupt, reset, queueing, microcode loading, and SCSI command construction paths defined earlier in `advansys.c`, along with the type definitions for `ASC_DVC_VAR`, `ADV_DVC_VAR`, `ASCEEP_CONFIG`, the three `ADVEEP_*_CONFIG` layouts, and `struct asc_board`.

## Purpose

The code translates detected AdvanSys adapter hardware into a registered Linux SCSI host:

- Populate narrow-board defaults, read EEPROM state, repair invalid EEPROM data when possible, and apply chip-specific queueing, SCSI ID, synchronous transfer, termination, and PCI erratum settings.
- Provide equivalent EEPROM defaulting and field mapping for wide PCI chips: ASC-3550, ASC-38C0800, and ASC-38C1600.
- Allocate wide-board DMA-visible carrier/request/scatter-gather memory and start the appropriate wide microcode driver.
- Build the `Scsi_Host` limits from board capabilities: target count, LUN count, command length, queue depth, scatter-gather table size, BIOS address, IRQ, and host ID.
- Probe VLB, EISA, and PCI adapters, claim their I/O or PCI resources, create per-channel `Scsi_Host` objects, call the common board setup path, and unwind resources on failures.
- Register and unregister the ISA/VLB, EISA, and PCI bus drivers at module load/unload.

## Important APIs, Types, and Functions

Narrow-board initialization centers on `ASC_DVC_VAR`, `ASC_DVC_CFG`, and `ASCEEP_CONFIG`. `AscInitAscDvcVar()` has already initialized the early fields before this range and this chunk completes the default state: queue counters, busy queue heads/tails, `dvc_cntl`, reset delay, `start_motor`, maximum DMA count, default SDTR/disconnect masks, host SCSI ID, chip version, and SDTR period table. PCI Ultra chips switch `bus_type` to `ASC_IS_PCI_ULTRA`, use `asc_syn_ultra_xfer_period`, increase `max_sdtr_index`, and program extra SCSI control bits with `AscSetExtraControl()`.

Narrow EEPROM access uses `AscWriteEEPCmdReg()`, `AscWaitEEPRead()`, `AscReadEEPWord()`, `AscGetEEPConfig()`, `AscWriteEEPDataReg()`, `AscWriteEEPWord()`, `AscSetEEPConfigOnce()`, and `AscSetEEPConfig()`. These functions drive the chip EEPROM command/data registers through the earlier `AscSetChipEEPCmd()`, `AscGetChipEEPCmd()`, `AscSetChipEEPData()`, and `AscGetChipEEPData()` helpers. The read/write paths deliberately handle mixed byte/word fields in `ASCEEP_CONFIG` with `le16_to_cpu()` and `cpu_to_le16()` so byte fields read through 16-bit EEPROM operations land in the expected in-memory order.

`AscInitFromEEP()` is the narrow-board configuration bridge. It stops the chip and queue executor, optionally resets the SCSI bus, validates the microcode PC address, reads and normalizes chip config registers, reads EEPROM, handles checksum failures, tests external LRAM with `AscTestExternalLram()`, clamps queue limits, resolves command-queueing/disconnect conflicts, extracts the adapter SCSI ID, initializes per-target DOS INT13 and SDTR fields, and may rewrite EEPROM after checksum recovery.

`AscInitGetConfig()` and `AscInitSetConfig()` are the public narrow-board configuration stages called by board discovery. `AscInitGetConfig()` checks the signature, initializes defaults, imports EEPROM state, records init state bits, clamps reset wait, and logs warning/error codes. `AscInitSetConfig()` revalidates the signature, cleans config bits, forces disconnects when command queueing is enabled, handles PCI-specific config register clearing and old PCI errata flags, sets the chip SCSI ID for non-PCI paths, and logs warnings/errors.

Wide-board EEPROM support uses static defaults and field-classification tables:

- `Default_3550_EEPROM_Config` and `ADVEEP_3550_Config_Field_IsChar`.
- `Default_38C0800_EEPROM_Config` and `ADVEEP_38C0800_Config_Field_IsChar`.
- `Default_38C1600_EEPROM_Config` and `ADVEEP_38C1600_Config_Field_IsChar`.

`AdvWaitEEPCmd()` polls `IOPW_EE_CMD` for `ASC_EEP_CMD_DONE` and calls `BUG()` if the chip never completes. `AdvReadEEPWord()` issues an EEPROM read command. `AdvSet3550EEPConfig()`, `AdvSet38C0800EEPConfig()`, and `AdvSet38C1600EEPConfig()` write config words, compute the checksum over `ADV_EEP_DVC_CFG_BEGIN` to `ADV_EEP_DVC_CFG_END - 1`, write the checksum word, write the control/OEM area, and disable writes. `AdvGet3550EEPConfig()`, `AdvGet38C0800EEPConfig()`, and `AdvGet38C1600EEPConfig()` read the same EEPROM layouts and convert character-classified fields.

`AdvInitFrom3550EEP()`, `AdvInitFrom38C0800EEP()`, and `AdvInitFrom38C1600EEP()` map wide EEPROM state into `ADV_DVC_VAR` and `ADV_DVC_CFG`. They repair checksum failures by copying the matching default EEPROM image, preserving the serial-number words read from EEPROM, and rewriting the EEPROM. They clamp `max_host_qng` and `max_dvc_qng` to driver-supported ranges, derive SDTR ability for 38C0800/38C1600 chips from packed four-target speed nibbles, decode termination policy, and return non-fatal warning bits. The 38C1600 path also adjusts Function 1 defaults: disables expansion ROM BIOS and derives INT A/INT B wiring from GPIO bit 0.

`AdvInitGetConfig()` is the wide-board get-config entry point. It records the PCI command parity bit into `control_flag`, reads chip version, validates the wide signature and `chip_type`, resets the chip, enables register writes, and dispatches to the chip-specific EEPROM init function.

The Linux SCSI integration point is `advansys_template`, whose callbacks are `.info = advansys_info`, `.queuecommand = advansys_queuecommand`, `.eh_host_reset_handler = advansys_reset`, `.bios_param = advansys_biosparam`, `.sdev_configure = advansys_sdev_configure`, and `.cmd_size = sizeof(struct advansys_cmd)`. The actual command and interrupt behavior behind these callbacks is earlier in the file; this chunk wires them into hosts allocated by `scsi_host_alloc()`.

Common board setup is in `advansys_board_found()`. It fills either `boardp->dvc_var.asc_dvc_var` for narrow boards or `boardp->dvc_var.adv_dvc_var` for wide boards, maps wide PCI BAR 1 with `pci_ioremap_bar()`, calls `AscInitGetConfig()` or `AdvInitGetConfig()`, snapshots EEPROM-derived fields into `boardp->eep_config` for procfs reporting, sets `Scsi_Host` limits, requests the IRQ, initializes chip microcode, registers the host with `scsi_add_host()`, and starts scanning with `scsi_scan_host()`.

Wide runtime memory is managed by `advansys_wide_init_chip()` and `advansys_wide_free_mem()`. The init path allocates coherent carrier memory with `dma_alloc_coherent()`, coherent request memory sized from `max_host_qng`, and a DMA pool for `adv_sgblk_t` blocks, then calls `AdvInitAsc3550Driver()`, `AdvInitAsc38C0800Driver()`, or `AdvInitAsc38C1600Driver()`. The free path releases the coherent areas and DMA pool and nulls their pointers.

Bus integration is split across VLB/ISA, EISA, and PCI:

- `_asc_def_iop_base[]`, `advansys_vlb_irq_no()`, `advansys_vlb_probe()`, `advansys_vlb_remove()`, and `advansys_vlb_driver` handle legacy VLB adapters through `isa_register_driver()`.
- `advansys_eisa_table`, `struct eisa_scsi_data`, `advansys_eisa_irq_no()`, `advansys_eisa_probe()`, `advansys_eisa_remove()`, and `advansys_eisa_driver` handle one or two EISA channels per device.
- `advansys_pci_tbl`, `advansys_set_latency()`, `advansys_pci_probe()`, `advansys_pci_remove()`, and `advansys_pci_driver` handle supported PCI device IDs and flag ABP940UW/38C0800/38C1600 devices as wide boards.

## Control Flow

For a narrow board, probe enters from the relevant bus probe and calls `advansys_board_found()`. The board-private `ASC_DVC_VAR` points at its `ASC_DVC_CFG`, records the I/O port, and records the detected bus type. The IRQ sharing policy is selected from the bus type. `AscInitGetConfig()` then verifies the signature, initializes defaults, and calls `AscInitFromEEP()`.

`AscInitFromEEP()` first forces the chip into a safe stopped state. It writes a halt marker in LRAM, stops queue execution, stops or resets the chip/SCSI bus if required, and fails if the chip is not halted or the program counter cannot be set to `ASC_MCODE_START_ADDR`. It then reads chip config registers and clears bits that must not persist. EEPROM import reads the checksum-covered fields and final checksum word. Auto-config state can override EEPROM config-lsw/config-msw for old chip version 3 boards.

After EEPROM import, checksum mismatch has two paths. PCI Ultra 3050 EEPROM-less boards receive hardcoded defaults and an adapter-info marker `0xBB`. Other narrow boards set `write_eep`, warn, continue with the read buffer, and later call `AscSetEEPConfig()` to rewrite the EEPROM with normalized values. Queue counts are adjusted for boards without external LRAM, bounded to `ASC_MIN_TOTAL_QNG` and `ASC_MAX_TOTAL_QNG`, and per-device tag queueing is bounded between `ASC_MIN_TAG_Q_PER_DVC` and total queue depth. Command queueing forces disconnect enablement for matching targets, the host SCSI ID is masked to `ASC_MAX_TID`, Ultra boards without Ultra SDTR enabled use the 10 MB/s minimum SDTR index, and each target receives its default SDTR period/offset.

`AscInitSetConfig()` runs after the EEPROM snapshot is stored in `boardp->eep_config.asc_eep`. It re-clears config bits, repeats the queueing/disconnect consistency check, records auto-config warnings, and for PCI boards clears low config bits and marks old 1200A/ABP940 chips with `ASC_BUG_FIX_IF_NOT_DWB` and `ASC_BUG_FIX_ASYN_USE_SYN`. Non-PCI paths set the chip SCSI ID directly.

For a wide board, `advansys_board_found()` fills `ADV_DVC_VAR`, identifies the chip type from the PCI device ID, maps PCI BAR 1 for memory-mapped register access, saves the legacy I/O port for reporting, and calls `AdvInitGetConfig()`. That function samples PCI parity behavior, validates chip identity, resets the chip, allows register writes, and dispatches to the chip-specific EEPROM import. The chip-specific import either trusts the EEPROM checksum or loads defaults and rewrites EEPROM, then maps wide transfer, queue, termination, BIOS, SCSI ID, and serial fields into `ADV_DVC_VAR`.

After board-specific configuration, `advansys_board_found()` snapshots EEPROM-derived settings into the board-private `eep_config` union. Narrow boards store `init_sdtr`, `disc_enable`, `use_cmd_qng`, start-motor, control, no-SCAM, queue, SCSI ID, max tag queue, and adapter-info values. Wide boards store the fields relevant to their chip family, including termination, BIOS control, WDTR/SDTR or SDTR-speed words, tag queueing, start motor, reset delay, and serial number.

The common SCSI host setup then sets `max_channel = 0`, target/LUN limits, maximum command length, `io_port`, `this_id`, `can_queue`, and `sg_tablesize`. Narrow `sg_tablesize` is derived from available queue blocks and `ASC_SG_LIST_PER_Q`; wide boards use `ADV_MAX_SG_LIST`. The value is capped at `SG_ALL`. BIOS address is read either through `AscGetChipBiosAddress()` for narrow boards or from wide LRAM BIOS fields, with a valid `0x55AA` signature causing the x86 real-mode code segment to be shifted left four bits into `shost->base`.

IRQ registration happens before chip microcode initialization. If `request_irq()` fails, setup unwinds mapped wide memory and returns an error to the bus probe. Narrow boards allocate `overrun_buf`, then call `AscInitAsc1000Driver()`. An initialization warning/error is tolerated only if `overrun_dma` was set; otherwise setup fails. Wide boards call `advansys_wide_init_chip()`, which allocates DMA resources and starts the chip-specific wide driver. On success, the host is registered with `scsi_add_host()` and scanning starts.

Release flows reverse the successful setup path. `advansys_release()` removes the SCSI host, frees the IRQ, unmaps and frees narrow overrun DMA/buffer or wide MMIO/DMA resources, then drops the host reference with `scsi_host_put()`. Bus remove functions also release bus-owned I/O regions or PCI regions and disable the PCI device.

VLB probing iterates a fixed I/O-port table through the ISA driver core. It claims the I/O region, checks the narrow signature and VLB chip-version maximum, allocates a host, decodes the IRQ from CfgLsw bits 2:4, and calls `advansys_board_found()` with `ASC_IS_VL`.

EISA probing allocates `struct eisa_scsi_data`, starts at `base_addr + 0xc30`, and checks up to two channels separated by `0x20`. Each present channel claims an I/O region, verifies the signature, performs an unexplained `inw(ioport + 4)` compatibility read, decodes a shared IRQ from CfgLsw bits 8:10, allocates a host, and calls `advansys_board_found()` with `ASC_IS_EISA`. A successfully initialized channel is saved in `data->host[i]`; removal walks both hosts.

PCI probing enables the device, claims PCI regions, enables bus mastering, adjusts the latency timer, requires BAR 0 to be non-empty for the I/O port, allocates a host, stores IRQ/device pointers, marks wide boards by device ID, and calls `advansys_board_found()` with `ASC_IS_PCI`. Wide boards also require BAR 1 mapping inside the common setup path.

Module init registers the VLB/ISA driver first, then the EISA driver, then the PCI driver. Failures unwind previously registered bus drivers. Module exit unregisters in reverse bus order: PCI, EISA, then ISA.

## State and Persistence

The key persistent hardware state is EEPROM content. Both narrow and wide paths read EEPROM into typed config structures, compute checksums over defined word ranges, and may rewrite EEPROM when a checksum mismatch is found. Narrow non-EEPROM-less checksum failures trigger a rewrite after normalized values are applied. Wide checksum failures copy default EEPROM images, preserve serial-number words, and write the defaults back to the board. These rewrites outlive the driver and are the most durable side effect in this chunk.

Runtime state lives mostly in `struct asc_board`, allocated as SCSI host private data. It owns the `ASC_DVC_VAR` or `ADV_DVC_VAR`, matching config union, EEPROM snapshot union, IRQ, device pointer, host pointer, init target mask, queue bookkeeping, optional stats, narrow SDTR data, and wide MMIO/DMA resources. `advansys_board_found()` populates this state once at probe time and later code paths use it for queueing, interrupts, procfs reporting, device configuration, and release.

Narrow runtime state includes per-target queue counters and busy queue links, `cfg->sdtr_enable`, `cfg->disc_enable`, `cfg->cmd_qng_enabled`, per-target `cfg->max_tag_qng`, per-target `cfg->sdtr_period_offset`, `dos_int13_table`, `dvc_cntl`, `start_motor`, `no_scam`, `max_total_qng`, `min_sdtr_index`, and chip-specific bug-fix flags. The chunk also configures chip registers such as config MSW/LSW, extra control, host interrupt enablement via EEPROM cfg-lsw normalization, and SCSI ID.

Wide runtime state includes `chip_type`, memory-mapped `iop_base`, `control_flag`, chip version, transfer capability masks, packed SDTR speed words, queue limits, termination setting, BIOS control, SCSI ID, start motor, reset delay, no-SCAM flag, serial fields, coherent carrier/request memory, and the SG DMA pool. The 38C1600 EEPROM recovery path persists function-specific ROM and interrupt wiring policy in EEPROM defaults.

Linux-visible state is also persisted in `Scsi_Host`: queue depth, target/LUN limits, command length, SG table size, BIOS base, IRQ, host ID, I/O port, DMA channel marker, and callback table. Once `scsi_add_host()` and `scsi_scan_host()` succeed, the SCSI midlayer owns discovery and command dispatch through the callbacks wired in this chunk.

## Dependencies and Integration Points

This chunk depends on low-level register helpers and chip-control code defined earlier in the same file: narrow `Asc*` I/O helpers, wide `AdvRead*`/`AdvWrite*` register and LRAM macros, queue/microcode initialization (`AscInitAsc1000Driver()`, `AdvInitAsc3550Driver()`, `AdvInitAsc38C0800Driver()`, `AdvInitAsc38C1600Driver()`), interrupt handling (`advansys_interrupt`), reset handling (`advansys_reset`), command queueing (`advansys_queuecommand`), device configuration (`advansys_sdev_configure`), and BIOS geometry (`advansys_biosparam`).

Kernel subsystem integration points include:

- SCSI core: `scsi_host_alloc()`, `scsi_add_host()`, `scsi_scan_host()`, `scsi_remove_host()`, `scsi_host_put()`, `struct scsi_host_template`, and `struct Scsi_Host` limits.
- IRQ core: `request_irq()` and `free_irq()`, with VLB using non-shared IRQs and EISA/PCI using `IRQF_SHARED`.
- DMA API: `dma_alloc_coherent()`, `dma_free_coherent()`, `dma_pool_create()`, `dma_pool_destroy()`, `dma_unmap_single()`, and the narrow overrun buffer path initialized by earlier code.
- PCI core: `pci_enable_device()`, `pci_request_regions()`, `pci_set_master()`, `pci_ioremap_bar()`, `pci_read_config_word()`, `pci_read_config_byte()`, `pci_write_config_byte()`, `pci_set_drvdata()`, `pci_release_regions()`, and `pci_disable_device()`.
- ISA/VLB and EISA bus cores: `isa_register_driver()`, `isa_unregister_driver()`, `struct isa_driver`, `eisa_driver_register()`, `eisa_driver_unregister()`, `struct eisa_driver`, `MODULE_DEVICE_TABLE(eisa, ...)`, and EISA base-address probing.
- I/O resource management: `request_region()`, `release_region()`, port I/O (`inw()`, `inp()`, `inpw()`), and MMIO unmapping with `iounmap()`.
- Module and firmware metadata: `module_init()`, `module_exit()`, `MODULE_DEVICE_TABLE(pci, ...)`, `MODULE_DESCRIPTION`, `MODULE_LICENSE`, and `MODULE_FIRMWARE()` declarations for narrow and wide microcode blobs.

The procfs display path is an indirect integration point. This chunk snapshots EEPROM data into `boardp->eep_config` specifically so `/proc/scsi/advansys/[0...]` reporting code earlier in the file can show the board configuration.

## Risks and Edge Cases

- EEPROM rewrite is persistent and hardware-facing. Checksum recovery paths can modify adapter EEPROM during probe. A bad default table, wrong field endian marker, or incorrect checksum range would persist broken configuration beyond module unload.
- `AdvWaitEEPCmd()` calls `BUG()` if EEPROM command completion never appears. A wedged or absent EEPROM on a wide board can panic the kernel rather than failing probe gracefully.
- `AscTestExternalLram()` writes test pattern `0x55AA` to the queue address for queue number 241 and restores it only when the readback succeeds. If the write partially works but readback fails, the saved word is not restored.
- Several paths use busy waits with `mdelay()`, including narrow SCSI reset waits up to seconds and EEPROM write delays. Probe can block CPU time for legacy hardware operations.
- Narrow checksum mismatch recovery is asymmetric. EEPROM-less PCI Ultra 3050 boards get known defaults, but other checksum failures continue using the read buffer before rewrite. If the read buffer contains severe corruption, normalized bounds cover queue fields but not every policy field.
- Warning code handling in `AscInitGetConfig()` and `AscInitSetConfig()` uses a `switch` over exact warning values, but `warn_code` is a bitmask. Multiple simultaneous warning bits fall through to "unknown warning" instead of printing each constituent condition.
- The narrow PCI branch in `AscInitSetConfig()` does not call `AscSetChipScsiID()` because the `else` binds to the non-PCI case. Correctness depends on PCI chip SCSI ID being set by config register/EEPROM paths.
- `advansys_wide_init_chip()` reports all allocation failures as "kmalloc() failed" and does not immediately free any resources allocated before a later allocation failure. The caller's `err_free_mem` path calls `advansys_wide_free_mem()`, so this relies on the common unwind path being used.
- `advansys_release()` always calls `dma_unmap_single()` for narrow `overrun_dma`. If release were reached after a partially initialized narrow board without a valid mapping, this could be unsafe; normal successful probe initializes it through `AscInitAsc1000Driver()`.
- EISA failure cleanup uses `kfree(data->host[0])` and `kfree(data->host[1])` instead of `scsi_host_put()` for already allocated host structures on the final `free_data` path. This is suspicious because successful `scsi_host_alloc()` objects should be released through the SCSI host API.
- EISA channel probing breaks out after a failure following a present/signature-matching channel. Later possible channels are not tried after that point.
- VLB `advansys_vlb_irq_no()` and EISA `advansys_eisa_irq_no()` can return `0` for invalid encoded IRQs, but the later common path still attempts `request_irq(0, ...)`.
- Wide boards require PCI BAR 1 mapping. If BAR 0 is present but BAR 1 is absent or cannot be mapped, probe fails after the host has been allocated and must rely on the common/bus unwind paths.
- `advansys_set_latency()` forces old PCI chips to latency timer 0 and raises other chips to at least `0x20`; this is hardware-policy-sensitive and may interact with platform PCI quirks.
- Module init registers legacy ISA/VLB before EISA and PCI. A failure in later bus registration unwinds earlier registrations, but any already probed device side effects depend on bus-core unregister behavior.

## Test and Validation Signals

Useful validation signals for this chunk are mostly probe/remove and hardware-facing:

- Build coverage with `CONFIG_PCI`, EISA, and ISA/VLB combinations should catch compile-time gating around wide-board code and legacy bus drivers.
- PCI probe on supported IDs should show successful `pci_enable_device()`, region claim, bus mastering, latency setup, BAR 0 I/O presence, wide-board flagging for ABP940UW/38C0800/38C1600, and BAR 1 MMIO mapping for wide boards.
- Narrow probe should log a valid signature, EEPROM checksum result, chip version, bounded queue depth, SCSI ID, SG table size, successful IRQ request, `AscInitAsc1000Driver()` result, `scsi_add_host()` success, and scan start.
- Wide probe should log valid chip ID/signature, chip type, EEPROM checksum/default recovery status, queue limits, termination mapping, successful coherent carrier/request allocation, SG DMA pool creation, chip-specific `AdvInitAsc*Driver()` result, host registration, and scan start.
- EEPROM checksum injection or hardware with bad EEPROM should exercise default recovery and verify that serial-number words are preserved on wide boards, queue limits are sane, and warning reporting is understandable.
- Endianness-sensitive tests should verify that byte-classified EEPROM fields such as SCSI ID, reset delay, queue limits, termination bytes, and OEM name bytes read and write identically on big-endian and little-endian builds.
- LRAM-size tests should cover narrow boards with and without external LRAM, confirming fallback queue depths (`ASC_MAX_PCI_ULTRA_INRAM_TOTAL_QNG`, `ASC_MAX_PCI_INRAM_TOTAL_QNG`) and config MSW changes.
- IRQ error injection should confirm that `request_irq()` failures release MMIO mappings and bus-owned regions and that invalid VLB/EISA IRQ encodings do not leave claimed regions behind.
- DMA allocation failure injection for wide boards should verify that carrier, request, and SG pool resources are freed by `advansys_wide_free_mem()` through the common error path.
- `scsi_add_host()` failure injection should free IRQs, narrow overrun memory or wide DMA resources, and mapped MMIO.
- Remove/unload tests should verify `scsi_remove_host()`, IRQ freeing, DMA unmap/free, `iounmap()`, PCI region release, PCI disable, VLB/EISA `release_region()`, and final `scsi_host_put()`.
- EISA multi-channel hardware or emulation should validate that both channels can register independent `Scsi_Host` instances, share the decoded IRQ correctly, and remove cleanly.
- Runtime SCSI smoke tests after probe should include device discovery, tagged queueing/disconnect behavior, synchronous/wide transfer negotiation from EEPROM settings, host reset through the SCSI error-handler callback, and module unload under idle and after I/O error conditions.
