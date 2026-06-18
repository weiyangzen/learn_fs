# subset-b-001038 research

This grouped report covers Linux libata PATA host drivers under `sources/distributed-fs/ceph-client/drivers/ata/`. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_acpi.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_acpi.c

Purpose: generic PCI IDE/libata driver that relies on ACPI `_GTM`/`_STM` methods to discover, filter, and program PATA timing modes. It binds broadly to PCI IDE-class devices and is useful when chipset-specific drivers are absent but ACPI exposes usable timing control.

Important APIs and control flow: `struct pata_acpi` caches the last ACPI timing block, the last selected device, and per-device transfer masks. `pacpi_port_start` requires an ACPI handle, allocates private state, discovers masks with `pacpi_discover_modes`, and then starts BMDMA. Reset goes through `pacpi_pre_reset`, which refreshes `_GTM` and delegates to `ata_sff_prereset`. `pacpi_mode_filter`, `pacpi_cable_detect`, `pacpi_set_piomode`, and `pacpi_set_dmamode` convert between libata mode choices and ACPI timing fields. `pacpi_qc_issue` reloads timings on device switches when ACPI reports non-independent master/slave timing.

State, dependencies, and risks: persistent state is only per-port devm-managed `struct pata_acpi`; ACPI firmware owns the durable timing behavior. Dependencies are PCI IDE probing, libata BMDMA/SFF helpers, ACPI handles on `ap->tdev`, and `ata_acpi_gtm`/`ata_acpi_stm`. Risks are firmware methods that accept a mode but silently coerce it, broad PCI class matching that can overlap chipset drivers, and shared-timing devices needing per-command reprogramming. Test signals are ACPI `_GTM` success at reset, mode masks matching expected firmware limits, correct 40/80-wire cable selection from discovered UDMA masks, successful suspend/resume through generic PCI PM, and I/O across master/slave switches without timing regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ali.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_ali.c

Purpose: chipset-specific ALi/ULi M5228/M5229 PATA driver for many 15x3 southbridge revisions, including early PIO-only parts, later MWDMA/UDMA parts, cable-detect quirks, ATAPI DMA policy, and resume-time chipset reinitialization.

Important APIs and control flow: module parameter `atapi_dma` controls whether ATAPI DMA is allowed. The global `ali_isa_bridge` is found at module init and used for bridge-specific workarounds. Cable handling combines DMI/subsystem overrides in `ali_cable_override` with C2+ config register detection in `ali_c2_cable_detect`. Timing setup flows through `ali_set_piomode`, `ali_set_dmamode`, FIFO management in `ali_fifo_control`, and `ali_program_modes`, with peer-device timing merges for shared command/8-bit timing. `ali_20_filter`, `ali_check_atapi_dma`, `ali_warn_atapi_dma`, and `ali_lock_sectors` constrain unreliable legacy behavior. `ali_init_one` chooses `ata_port_info` by PCI revision, calls `ali_init_chipset`, optionally upgrades rev 0x20 controllers when the ISA bridge indicates UDMA support, and selects SFF or BMDMA registration.

State, dependencies, and risks: state is mostly PCI config registers plus the retained ISA bridge reference and module parameter. Dependencies include DMI, PCI revision/subsystem IDs, libata BMDMA32/SFF ops, and ALi north/south bridge companion registers. Risks include NDA-derived timing knowledge, conservative ATAPI DMA disablement, old-controller LBA48 forced through PIO by `ATA_FLAG_PIO_LBA48`, and bridge tri-state toggling in `ali_c2_c3_postreset`. Test signals are revision-specific mode masks, cable override systems reporting short 40-wire rather than limiting incorrectly, warning output for ATAPI DMA policy, successful C2/C3 post-reset on ALi 1533 bridge systems, and resume restoring register bits through `ali_reinit_one`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ali.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_amd.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_amd.c

Purpose: AMD and NVIDIA PCI PATA driver covering AMD 7401/7409/7411/7441/8111/CS5536-compatible IDE functions plus NVIDIA nForce PATA variants. It programs timing registers, cable detection, FIFO policy, NVIDIA BIOS-mode filtering, and resume recovery.

Important APIs and control flow: `timing_setup` is the shared timing engine for AMD and NVIDIA register layouts, computing `ata_timing` values, merging peer 8-bit timing, and programming setup, 8-bit, drive, and UDMA timing fields at either offset `0x40` or `0x50`. AMD reset and cable paths use `amd_pre_reset`, `amd_cable_detect`, and `amd_fifo_setup`; NVIDIA paths use `nv_pre_reset`, `nv_mode_filter`, and `nv_host_stop`. Port operation tables encode clock generations: 33, 66, 100, and 133 style AMD, plus 100/133 NVIDIA. `amd_init_one` selects the `ata_port_info` by PCI ID and revision, applies Serenade and early-7409 quirks, clears simplex/FIFO where needed, caches NVIDIA UDMA BIOS register `0x60` as host private data, and activates BMDMA.

State, dependencies, and risks: state is the PCI config timing/FIFO state and, for NVIDIA, cached BIOS UDMA data stored as `host->private_data` and restored by `nv_host_stop`. Dependencies are PCI IDs/revisions, ACPI GTM for NVIDIA mode filtering, libata BMDMA32/BMDMA helpers, and platform BIOS setup quality. Risks are unreliable NVIDIA cable detection, relying on BIOS/ACPI limits to avoid bad UDMA choices, shared FIFO disabling for ATAPI and broken AMD 7411 FIFO, and board-specific Serenade UDMA limiting. Test signals include correct probe type selection, NVIDIA debug traces showing BIOS/ACPI mask intersection, FIFO clearing at init/resume, port enable-bit handling during reset, and stable DMA after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_arasan_cf.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_arasan_cf.c

Purpose: platform driver for the Arasan CompactFlash controller in True IDE mode. It supports PIO and optional MWDMA/UDMA using an external DMA engine, card-detect interrupts, runtime controller reset, and platform/OF binding for `"arasan,cf-spear1340"`.

Important APIs and control flow: `struct arasan_cf_dev` carries MMIO base, physical base, clock, ATA host, IRQ, card state, DMA channel/completions, work items, and active queued command. `cf_init` enables the clock, sets the interface clock, enables True IDE mode, card detect IRQ, and global CF IRQ; `cf_exit` disables interrupts, resets the card, clears host enable, and disables the clock. `arasan_cf_probe` maps resources, applies platform quirks (`CF_BROKEN_*`), builds a single ATA port, fills taskfile MMIO addresses, initializes completions/work, calls `cf_init`, detects initial card presence, and activates the host. DMA commands enter through `arasan_cf_qc_issue`, which loads the taskfile, stores `acdev->qc`, and schedules `data_xfer`; `data_xfer`, `sg_xfer`, `dma_xfer`, `wait4buf`, and `arasan_cf_interrupt` coordinate FIFO availability, transfer completion, and DMA-engine memcpy operations. Error paths use `arasan_cf_freeze`, `arasan_cf_error_handler`, controller reset, and delayed finish polling when BUSY/DRQ remains set.

State, dependencies, and risks: persistent driver state is per-device `struct arasan_cf_dev`, hardware interrupt masks/status, `card_present`, completions, workqueue state, and active `qc`. Dependencies include platform resources, optional platform data, a clock, DMA engine channel named `"data"`, libata SFF helpers, and shared global IRQ registers also used by Arasan XD. Risks include PIO-only fallback when IRQ is missing, defaulting to broken UDMA on platforms without pdata, asynchronous work racing with remove/suspend if not cancelled, 3-second timeout assumptions, and shared global interrupt enable/clear behavior. Test signals are card insertion/removal causing `ata_ehi_hotplugged` and port freeze, DMA read/write completion through BUF_AVAIL/XFER_DONE IRQs, PIO error IRQ producing host-bus errors, suspend terminating active DMA and restarting on resume, and correct disabling of mode masks by platform quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_arasan_cf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_artop.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_artop.c

Purpose: ARTOP/Acard ATP8xx PCI PATA driver for 6210, 6260/626x, and 628x controllers. It handles variant-specific PIO/DMA timing layouts, old 6210 channel serialization, cable detection for newer parts, and Macintosh/BIOS fixups.

Important APIs and control flow: `artop62x0_pre_reset` checks per-port enable bits for odd device IDs before SFF reset. `artop6210_load_piomode` and `artop6260_load_piomode` program different timing register formats, while matching `set_piomode` and `set_dmamode` callbacks clear or install UDMA nibbles. `artop6210_qc_defer` serializes commands across both host ports for the older 6210. `atp8xx_fixup` clears stale UDMA/test bits, raises PCI latency, and enables IRQ/burst mode for affected devices. `artop_init_one` enables the PCI device, chooses a port-info profile from `driver_data` and a fast 628x BAR4 bit, applies fixups, and uses `ata_pci_bmdma_init_one`; resume repeats the fixup before `ata_host_resume`.

State, dependencies, and risks: state lives in PCI config registers and the global `clock` selector, currently fixed to 33 MHz timing table index 0. Dependencies are PCI IDs, libata BMDMA/SFF reset, and BAR4 status for 628x speed capability. Risks are the unimplemented clock detection path, old 6210 serialization bottlenecks, variant-specific register maps, and relying on PCI latency/IRQ fixups on firmware that left cards partially initialized. Test signals are correct 6210 command deferral under dual-port load, 6260 cable detect, 628x UDMA5/6 profile selection, resume restoring burst/IRQ settings, and no stale UDMA bits before libata probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_artop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_atiixp.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_atiixp.c

Purpose: ATI/AMD IXP PCI PATA driver for IXP200/300/400/600/700 and Hudson2 IDE functions. It programs PIO/MWDMA/UDMA timing registers, handles enable-bit reset gating, works around cable-detect limits, and controls per-command UDMA enable bits around BMDMA transfers.

Important APIs and control flow: `atiixp_cable_detect` uses DMI override for MSI E350DM-E33 and otherwise infers cable class from BIOS-programmed UDMA mode nibbles. `atiixp_prereset` suppresses disabled ports using config register `0x48`. Timing writes are serialized by `atiixp_lock`; `atiixp_set_pio_timing`, `atiixp_set_piomode`, and `atiixp_set_dmamode` update PIO mode/timing, MWDMA timing, UDMA mode fields, and matching PIO requirements. `atiixp_bmdma_start` sets the per-device UDMA control bit immediately before DMA; `atiixp_bmdma_stop` clears it after completion. `atiixp_init_one` creates one or two port infos, using a dummy secondary port for SB600, and requests parallel scan.

State, dependencies, and risks: persistent state is PCI config timing/control registers; synchronization is via a static spinlock. Dependencies are PCI IDs, DMI, libata BMDMA ops, and the controller's shared timing registers. Risks include BIOS-mode based cable detection rather than physical detection, global spinlock serialization across controllers, potential UDMA-control misprogramming if BMDMA callbacks are bypassed, and SB600 secondary-port absence. Test signals include correct primary-only enumeration on IXP600, UDMA control bit toggling during DMA, DMI short-cable override, port-disabled resets returning `-ENOENT`, and mixed PIO/MWDMA mode timing stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_atiixp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_atp867x.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_atp867x.c

Purpose: PCI driver for ARTOP/Acard ATP867A/B 64-bit, four-channel UDMA133 controllers. It manually maps the controller's single I/O BAR, initializes four native libata ports, and programs per-port hot timing registers.

Important APIs and control flow: `struct atp867x_priv` caches per-port MMIO pointers for DMA mode and PIO speed registers plus detected 66 MHz PCI state. `atp867x_set_priv` initializes this per-port cache; `atp867x_set_piomode` computes `ata_timing` at 33 MHz with quarter-cycle UDMA timing, clears UDMA mode for the target device, and writes master/slave/eight-bit PIO clocks. `atp867x_set_dmamode` programs UDMA nibbles and intentionally lowers modes on 66 MHz PCI per silicon guidance. `atp867x_fixup` raises PCI latency, initializes port speed and preread counters, enables interrupts and burst mode, and sets Rev-B slow UDMA5. `atp867x_ata_pci_sff_init_host` maps BAR0, fills SFF/BMDMA addresses for all four ports, sets private data, applies fixup, and configures the DMA mask. `atp867x_init_one` allocates four ports and activates shared IRQ BMDMA.

State, dependencies, and risks: state is per-port `atp867x_priv`, BAR0 MMIO registers, PCI latency/sys-info, and shared host iomap. Dependencies are PCI device IDs, libata BMDMA/SFF helpers, DMA mask support, and BAR0 availability. Risks are unknown cable detection except for subsystem short-cable override, shared MWDMA/clock side effects across devices, per-device UDMA downshifting on 66 MHz buses, and direct four-port address construction from one BAR. Test signals are all four ports described/activated, per-port debug address output, Rev-B slow UDMA5 bit set, 66 MHz systems downshift as expected, and resume reapplies the fixup before host resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_atp867x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_buddha.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_buddha.c

Purpose: Amiga Zorro PIO-only driver for Individual Computers Buddha, Catweasel, and X-Surf IDE interfaces. It maps Zorro board address layouts into libata SFF ports and uses Amiga shared port interrupts.

Important APIs and control flow: fixed base tables describe Buddha/Catweasel three-port and X-Surf two-port layouts. `pata_buddha_data_xfer` performs raw 16-bit word transfers and handles trailing bytes. `pata_buddha_set_mode` forces all detected devices to PIO0 without reprogramming hardware. `pata_buddha_irq_check` reads board IRQ status; `pata_xsurf_irq_clear` acknowledges X-Surf. `pata_buddha_probe` requests board regions, preserves existing X-Surf drvdata because the network driver may use the same Zorro device, allocates an ATA host with two or three ports, fills register addresses with Amiga spacing, stores per-port IRQ status address in `ap->private_data`, and activates on `IRQ_AMIGA_PORTS`. `pata_buddha_late_init` registers normal Zorro IDs and manually probes X-Surf boards to avoid modalias conflict.

State, dependencies, and risks: state is Zorro resource ownership, host drvdata, per-port IRQ status pointer, and optional X-Surf drvdata preservation. Dependencies include Amiga Zorro APIs, `ZTWO_VADDR`, `z_readb`/`z_writeb`, raw word I/O helpers, and shared Amiga port interrupts. Risks include X-Surf resource request fallback with an empty failure branch for the second region, manual late binding outside normal modalias ownership, no DMA/IORDY, and forced PIO0 even though `pio_mask` advertises PIO4. Test signals are board-specific port count and register offsets, no regression with zorro8390 on X-Surf, IRQ check/clear behavior on shared Amiga interrupt, and successful odd-byte PIO transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_buddha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cmd640.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_cmd640.c

Purpose: PCI CMD640 PIO-only PATA driver. It supports the PCI variant, disables unsafe prefetch/FIFO behavior, and handles the controller's awkward shared timing on the secondary channel.

Important APIs and control flow: `struct cmd640_reg` stores the last secondary device and saved `DRWTIM23` active/recovery values. `cmd640_set_piomode` computes PIO timings, clamps them into CMD640 register encoding, writes primary-device timings directly, and stores secondary per-device data for command-time switching. `cmd640_qc_issue` reloads `DRWTIM23` when the active secondary device changes, then delegates to `ata_sff_qc_issue`. `cmd640_port_start` allocates timing state. `cmd640_sff_irq_check` reads CFR/ARTIM23 interrupt bits. `cmd640_hardware_init` clears prefetch-related state, sets command timing and burst size, and disables risky FIFOs before `ata_pci_sff_init_one` activates the device.

State, dependencies, and risks: state is per-port timing cache and PCI config register programming. Dependencies are PCI SFF libata support, CMD640 config layout, and PIO32 data transfers. Risks include ancient hardware data-corruption errata, secondary channel shared timing requiring per-command updates, PCI-only coverage despite VLB hardware history, and 40-wire-only cable policy. Test signals are `port_start` private allocation, secondary master/slave switching writes `DRWTIM23`, IRQ status bits match channel interrupts, resume repeats hardware init, and PIO transfers avoid FIFO/prefetch corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cmd640.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cmd64x.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_cmd64x.c

Purpose: PCI CMD64x-family PATA driver for CMD643/646/648/649 controllers. It provides variant-specific DMA capabilities, IRQ handling, cable detection, port-enable checks, and resume fixups.

Important APIs and control flow: `cmd64x_set_timing` computes and encodes PIO/MWDMA timing using per-port/per-device register maps and shared secondary setup timing. `cmd64x_set_dmamode` programs UDMA timing/control bits or falls back to MWDMA timing. IRQ handling differs by generation: `cmd64x_sff_irq_check`/`clear` use CFR/ARTTIM23, while `cmd648_sff_irq_check`/`clear` use BAR4 MRDMODE. `cmd64x_fixup` sets latency, IRQ mode, memory-read-line, and PPC-specific UDMA defaults. `cmd64x_init_one` selects port info by device and CMD646 revision, disables simplex for CMD643, handles Mobility Electronics bridges that misreport port enables, turns disabled ports into dummy ports, and activates BMDMA. `cmd64x_reinit_one` reapplies fixup on resume.

State, dependencies, and risks: state is PCI config and BAR4 I/O registers; there is no driver-private heap state. Dependencies are PCI revision IDs, libata BMDMA, port-enable bits, and optional CONFIG_PPC behavior. Risks include known broken UDMA on early CMD646 revisions, interrupt status clear-by-read semantics, bridge misreporting of port enable bits, and shared timing on secondary channel. Test signals are CMD646 revision classification, cable detect on CMD648/649, disabled-port notice and dummy-port behavior, MRDMODE interrupt clear on newer parts, and resume maintaining latency/IRQ fixup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cmd64x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cs5520.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_cs5520.c

Purpose: experimental Cyrix CS5510/CS5520 PATA driver for unusual hardware that performs bus mastering while drives remain in PIO timing mode. It manually maps legacy IDE ports and BMDMA BAR2 rather than relying on the standard PCI IDE BAR layout.

Important APIs and control flow: `cs5520_set_timings` and `cs5520_set_piomode` program controller PIO clocks from a small table. `cs5520_init_one` enables the PCI device, reads port enable/DMA bits from config `0x60`, builds dummy or live port infos, enables DMA mode if firmware disabled it, sets the MWDMA mask from PCI ID driver data, allocates the host, maps fixed legacy command/control ports plus BMDMA BAR2, fills SFF ports, starts the host, requests IRQ14/IRQ15 separately, and registers the host. Suspend/resume is custom: suspend saves PCI state without disabling the device, while resume restores DMA enable and resumes the host.

State, dependencies, and risks: state is PCI config `0x60`, fixed I/O port mappings, BMDMA BAR2, and legacy IRQ assignments. Dependencies include old ISA IDE port routing, devm I/O port maps, libata dumb BMDMA PRD support, and PCI DMA mask setup. Risks include experimental status, fixed IRQ14/15 assumptions, DMA on PIO-only drives, lack of public documentation, and nonstandard suspend logic to avoid disabling the multifunction device. Test signals are only enabled ports becoming active, BMDMA BAR mapping success, DMA-enable warning when firmware left it off, IRQ14/15 request success, and resume preserving I/O after sleep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cs5520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cs5530.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_cs5530.c

Purpose: Cyrix/NS/AMD CS5530 PATA driver for Geode companion systems. It initializes companion PCI master/legacy functions, programs memory-mapped timing registers, and handles the chip's single shared MWDMA/UDMA selection bit.

Important APIs and control flow: `cs5530_port_base` derives the timing MMIO window from the BMDMA address. `cs5530_set_piomode` selects one of two PIO timing formats based on a format bit and writes master/slave timing. `cs5530_set_dmamode` selects fixed timing values for UDMA0-2 and MWDMA0-2, preserves the format bit, sets the shared UDMA-vs-MWDMA bit, marks BMDMA capability, and stores the active DMA device in `ap->private_data`. `cs5530_qc_issue` reloads DMA timing when a command switches between devices using different DMA families. `cs5530_init_chip` finds the PCI master and legacy functions, enables master/MWI, disables Windows-style UDMA trapping, and writes sane burst/X-bus settings. `cs5530_init_one` applies Palmax DMI secondary-port PIO-only quirk and activates BMDMA.

State, dependencies, and risks: state is timing registers behind BMDMA space, `ap->private_data` as last DMA device, and companion function PCI config state. Dependencies are multiple Cyrix PCI functions, DMI, libata dumb BMDMA, and 40-wire policy. Risks are failing if companion functions are not discoverable, shared MWDMA/UDMA state requiring command-time reprogramming, Palmax docking DMA disablement, and resume failure being fatal. Test signals are `cs5530_init_chip` success, Palmax DMI log and secondary PIO-only behavior, correct BMDMA status capability bits, DMA family switches reprogramming timing, and resume reinitializing companion registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cs5530.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cs5535.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_cs5535.c

Purpose: NS/AMD CS5535 PATA driver for Geode systems where IDE timing controls live in model-specific registers rather than ordinary PCI config space.

Important APIs and control flow: `cs5535_cable_detect` reads PCI cable register `0x48`. `cs5535_set_piomode` uses `wrmsr` to program per-device PIO command/data timing MSRs, computes shared command timing from the slower device on the link, updates the peer timing if needed, and sets the DMA timing format bit. `cs5535_set_dmamode` reads the DMA timing MSR, preserves the PIO format bit, and writes fixed UDMA0-4 or MWDMA0-2 values. `cs5535_init_one` exposes only the primary port and registers through `ata_pci_bmdma_init_one`.

State, dependencies, and risks: state persists in Geode ATAC MSRs and PCI cable detect register. Dependencies include x86 MSR access through `<asm/msr.h>`, PCI IDs from NS/AMD, and libata BMDMA. Risks include MSR-only timing programming tying behavior to Geode-class CPUs, command timing shared between devices, no secondary port support, and UDMA limited to mode 4. Test signals are successful MSR read/write during mode setup, cable register reporting expected 40/80-wire state, peer command timing updates when mixed PIO devices exist, and primary-only host enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cs5535.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cs5536.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_cs5536.c

Purpose: AMD CS5536 PATA driver that programs virtualized PCI IDE timing registers with dword accesses, with an optional 32-bit x86 `msr=1` parameter to bypass broken BIOS virtualization and use Geode MSRs directly.

Important APIs and control flow: `cs5536_read` and `cs5536_write` abstract PCI config dword versus MSR access. `cs5536_cable_detect` reads IDE config cable bits. `cs5536_set_piomode` programs drive timing (`DTC`) and command/address timing (`CAST`), merging command timing across paired devices. `cs5536_set_dmamode` programs UDMA timing in `ETC`, or clears UDMA and programs MWDMA via `DTC`. `cs5536_init_one` checks a Bachmann OT200 DMI quirk that disables UDMA, validates channel enable, logs MSR mode if forced, exposes only the primary port, and registers BMDMA32 ops.

State, dependencies, and risks: state is in PCI virtual registers or MSRs depending on `use_msr`; no heap private state is used. Dependencies are PCI IDs, DMI, optional 32-bit x86 MSR access, and libata BMDMA32. Risks are firmware register virtualization bugs, `msr` parameter unavailable on non-32-bit x86, single-channel support, DMI-based UDMA disablement, and dword-only writes required to avoid unaligned virtualization issues. Test signals are channel enable rejection when BIOS disables IDE, DMI OT200 falling back to no-UDMA port info, cable detection from config bits, MSR mode logging, and stable mode programming on systems with broken PCI virtualization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cs5536.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cypress.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_cypress.c

Purpose: Cypress/Contaq CY82C693 PCI PATA driver for the primary ATA function. It provides PIO timing and optional MWDMA programming using both PCI config registers and legacy indexed I/O ports.

Important APIs and control flow: module parameter `enable_dma` controls whether MWDMA modes are advertised. `cy82c693_set_piomode` computes libata timings, encodes 16-bit and 8-bit active/recovery values, and writes master/slave setup and timing registers. `cy82c693_set_dmamode` writes the DMA mode through magic indexed ports `0x22/0x23` and sets timeout index `0x32` to `0x50`. `cy82c693_init_one` only accepts PCI function 1, leaves secondary magic function unhandled, and registers primary plus dummy secondary with BMDMA.

State, dependencies, and risks: state is PCI config timing registers, global indexed I/O ports, and static mutable `ata_port_info` updated by the DMA parameter. Dependencies are PCI function layout, libata BMDMA, and low I/O port access. Risks include only primary-channel support, global legacy index/data ports that can conflict on unusual systems, mutable static port info across probes, optional DMA whose reliability is parameter-controlled, and 40-wire-only cable policy. Test signals are function 1 binding only, `enable_dma=0` suppressing MWDMA, correct indexed DMA writes, primary port enumeration, and suspend/resume through generic PCI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_cypress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_efar.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_efar.c

Purpose: EFAR 9130 PIIX4-like PCI PATA driver with UDMA66 support. It follows Intel PIIX-style timing rules but uses EFAR-specific enable, cable, and UDMA register layouts.

Important APIs and control flow: `efar_pre_reset` checks per-channel enable bits in config registers `0x41/0x43`. `efar_cable_detect` reads cable state from `0x47`. `efar_set_piomode` serializes register updates with `efar_lock`, programs PPE/IORDY/TIME/SITRE and master/slave timing fields, and clears UDMA enable for the device. `efar_set_dmamode` either programs widened UDMA mode nibbles in `0x4A` and enables UDMA in `0x48`, or maps MWDMA onto PIO timing with DMA-only/IORDY/TIME controls. `efar_init_one` exposes two identical ports, MWDMA1/2 only plus UDMA4, and requests parallel scan.

State, dependencies, and risks: state is PCI config timing and UDMA-enable registers protected by a static spinlock. Dependencies are PCI EFAR ID, libata BMDMA, and PIIX timing semantics. Risks are clone-specific divergence from Intel behavior, shared spinlock across controllers, cable detect interpretation inverted from many controllers, and MWDMA depending on previously compatible PIO programming. Test signals are reset skipping disabled channels, UDMA4 mode programming in widened register fields, MWDMA with forced PIO timing when needed, 80-wire detection from `0x47`, and parallel scan of both ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_efar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ep93xx.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_ep93xx.c

Purpose: platform driver for Cirrus EP93xx SoC PATA hardware. It implements custom SFF taskfile access using controller GPIO-style IDE control registers, calibrated software PIO delays, and UDMA through two DMA-engine slave channels.

Important APIs and control flow: `struct ep93xx_pata_data` stores platform device, MMIO base, current PIO timing, IORDY use, UDMA data physical addresses, and RX/TX DMA channels. PIO access is built from `ep93xx_pata_rw_begin`, `ep93xx_pata_rw_end`, `ep93xx_pata_read/write`, and register/data wrappers; these drive IDECTRL lines and sample IORDY. Custom libata SFF callbacks implement status/altstatus, taskfile load/read, command execution, device select, devctl, PIO data transfer, device-presence probing, soft reset, and FIFO drain. DMA setup flows through `ep93xx_pata_dma_init`, `ep93xx_pata_dma_start`, `ep93xx_pata_dma_stop`, `ep93xx_pata_dma_status`, and `ep93xx_pata_dma_setup`, using `"rx"` and `"tx"` DMA channels and IDEUDMAOP enable sequencing. `ep93xx_pata_probe` maps MMIO, initializes DMA channels, clears registers, allocates a single ATA port, assigns UDMA mask based on SoC revision table, enables safe PIO0, and activates with `ata_bmdma_interrupt`.

State, dependencies, and risks: state includes current timing in `drv_data->t`, DMA channel handles, hardware IDECFG/IDECTRL/UDMA registers, and SoC revision-derived capabilities. Dependencies include platform IRQ/MMIO resources, DMA engine slave channels, `soc_device_match`, OF compatible `"cirrus,ep9312-pata"`, and EP93xx timing assumptions. Risks include software delay loops calibrated for 200 MHz maximum CPU speed, no hardreset callback, complex custom SFF behavior diverging from libata helpers, DMA transfer error reporting via UDMA status bits, and resource cleanup needing DMA release and register clear. Test signals include PIO register read/write correctness, IORDY timing on PIO3/4 devices, softreset detecting master/slave signatures, UDMA mask varying across E0/E1/E2 SoC revisions, DMA error bits becoming `ATA_DMA_ERR`, and remove clearing registers/releasing both channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ep93xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_falcon.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_falcon.c

Purpose: platform PIO driver for Atari Falcon and Q40/Q60 PATA interfaces. It maps platform-provided I/O or memory resources into libata SFF register addresses and handles Atari/Q40 byte-swapping behavior.

Important APIs and control flow: module parameter `data_swab` is a bitmap controlling per-drive byte swapping for ATA filesystem I/O. `pata_falcon_data_xfer` uses raw word I/O or swapped word I/O depending on device class, request type, and private swap mask, with trailing-byte handling. `pata_falcon_set_mode` forces enabled devices to PIO0 and marks them PIO-only. `pata_falcon_init_one` requests optional I/O resources and required memory resources, allocates one ATA port, computes Falcon versus Q40 offsets/shifts, fills taskfile/control addresses, stores the shifted swap mask in `ap->private_data`, and activates either interrupt-driven SFF or PIO polling if no IRQ exists.

State, dependencies, and risks: state is platform resources, `ap->private_data` swap bitmap, and optional IRQ. Dependencies include Atari/Q40 platform device creation, raw word I/O helpers, Atari interrupt headers, and libata SFF. Risks are PIO-only operation, per-board address assumptions, optional polling mode when IRQ is absent, pass-through commands bypassing swap behavior, and forced PIO0 despite PIO4 mask. Test signals are correct resource mapping for Falcon versus Q40, `data_swab` behavior per drive and request type, polling fallback log when IRQ is missing, odd-byte transfer handling, and successful platform remove via `ata_host_detach`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_falcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ftide010.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_ftide010.c

Purpose: platform driver for Faraday FTIDE010 PATA controllers, with optional Cortina Gemini SATA bridge integration. It provides BMDMA-style libata registration, PIO/MWDMA/UDMA timing tables, clock management, OF probing, and Gemini mux/cable policy.

Important APIs and control flow: `struct ftide010` stores device, MMIO base, peripheral clock, ATA host, cable types, and Gemini bridge mapping flags. `ftide010_set_piomode` writes PIO active/recovery timing. `ftide010_set_dmamode` selects master/slave clock and UDMA-enable bits, chooses 50/66 MHz timing tables for MWDMA/UDMA, handles special UDMA5/6 timing bits, and stores the currently programmed device in `ap->private_data`; `ftide010_qc_issue` reprograms DMA timing on master/slave switches. Base `pata_ftide010_port_ops` inherits BMDMA. Gemini-specific `pata_ftide010_gemini_init` looks up the shared SATA bridge, adjusts port ops for bridge start/stop/cable detect, sets `ATA_FLAG_SATA` where muxed, applies SQ201 PIO-only quirk, and derives cable/bridge mappings from mux mode. `pata_ftide010_probe` maps MMIO, enables optional `PCLK`, handles Gemini versus plain PATA cable setup, allocates a host, fills BMDMA/SFF addresses, logs device ID, and activates.

State, dependencies, and risks: state includes per-controller `ftide010`, mutable global port ops when Gemini is configured, clock enable state, and shared Gemini SATA bridge state. Dependencies are OF compatible `"faraday,ftide010"` and optionally `"cortina,gemini-pata"`, `sata_gemini` helpers, libata BMDMA, and platform IRQ/MMIO resources. Risks include mutable static port operations affecting multiple instances, shared clock/timing registers requiring command-time reprogramming, Gemini bridge start failing if no mapped bridge is active, SQ201 DMA disablement, and cable detect returning only the master cable type. Test signals are PCLK enable/disable symmetry, correct FTIDE010 register address mapping, DMA mode reprogramming on device switch, Gemini mux modes producing expected SATA/PATA cable flags, bridge start/stop logs, and device ID/IRQ probe output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_ftide010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_gayle.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_gayle.c

Purpose: Amiga Gayle platform PIO driver for A1200/A4000-style IDE interfaces. It maps Gayle board register spacing into libata SFF and handles the A1200 explicit interrupt acknowledgement path.

Important APIs and control flow: `pata_gayle_data_xfer` uses raw 16-bit transfers with trailing-byte support. `pata_gayle_set_mode` forces detected devices to PIO0 without hardware tuning. `pata_gayle_irq_check` reads `GAYLE_IRQ_IDE`; `pata_gayle_irq_clear` reads status and writes the Gayle IRQ clear value for explicit-ack systems. `pata_gayle_init_one` consumes `gayle_ide_platform_data`, requests the memory resource, allocates a single ATA port, selects A1200 or A4000 ops based on `explicit_ack`, fills Zorro-style register addresses and control register, stores IRQ port in `ap->private_data`, activates on `IRQ_AMIGA_PORTS`, and saves host drvdata.

State, dependencies, and risks: state is platform data, requested Gayle memory region, host drvdata, and per-port IRQ port pointer. Dependencies include Amiga hardware headers, `ZTWO_VADDR`, Gayle platform data, shared Amiga port IRQ, and libata SFF. Risks include PIO-only/no-IORDY behavior, forced PIO0, platform data assumptions, different IRQ acknowledgement requirements between A1200 and A4000, and no DMA support. Test signals are A1200/A4000 probe log style, IRQ check/clear behavior, correct register offset mapping, successful shared IRQ activation, and odd-byte transfer correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_gayle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_hpt366.c -->
# sources/distributed-fs/ceph-client/drivers/ata/pata_hpt366.c

Purpose: HighPoint HPT366/HPT368 PCI PATA driver for UDMA66-era controllers. It selects timing tables based on detected PCI clock, filters known-bad drive models, handles unusual one-channel-per-function enable/cable behavior, and initializes chipset PCI performance registers.

Important APIs and control flow: `struct hpt_clock` timing tables encode PIO/MWDMA/UDMA register values for 25, 33, and 40 MHz clocks. `hpt36x_find_mode` looks up the timing value stored in `host->private_data`. `hpt366_filter` blocks ATAPI DMA and limits or disables UDMA for specific problematic ATA model strings via `hpt_dma_broken`. `hpt36x_cable_detect` reads function-local config `0x5A` bit 1. `hpt366_set_mode` merges selected timing bits into per-device config dwords while disabling FIFO/PIO bus-master bits. `hpt366_prereset` validates both channel-enable bits and clears an MCR2 reset/state-machine bit before SFF reset. `hpt36x_init_chipset` sets cache line, latency, min/max grant, and forces both channels enabled if firmware enabled either. `hpt36x_init_one` rejects later HPT37x/30x revisions, chooses a timing table from config `0x40`, and registers a single-port BMDMA host per PCI function.

State, dependencies, and risks: state is PCI config timing/performance registers and the timing-table pointer in host private data. Dependencies are PCI IDs/revisions, libata BMDMA/SFF, model strings from IDENTIFY data, and one-channel-per-function hardware layout. Risks include blacklist drift for old drives, rejecting later chips that need other drivers, clock detection from existing timing register bits, forced channel enable side effects, and disabling FIFO/PIO_MST to improve error handling at performance cost. Test signals are revision >2 ignored, timing table selection for 25/33/40 MHz, cable detect limiting UDMA on 40-wire, blacklist messages and mask reductions for affected drives, and resume reapplying chipset init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/pata_hpt366.c -->
