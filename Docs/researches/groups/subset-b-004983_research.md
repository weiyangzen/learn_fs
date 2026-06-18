# Research Report: subset-b-004983

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/ntb_hw_idt.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/ntb_hw_idt.c

Purpose: Implements the IDT PCIe-switch NTB hardware driver as a standalone PCI driver and NTB provider. It supports IDT 89HPES NT switch families, discovers active NT endpoint peers, exposes NTB operations for link, memory windows, doorbells, and messages, registers hwmon temperature attributes, and adds a debugfs `info:<pci>` node.

Important APIs, types, and functions: The file builds static register tables `ntdata_tbl`, `portdata_tbl`, and `partdata_tbl` around the structures from `ntb_hw_idt.h`. `idt_nt_read/write()` access local NT-function config BAR0, while `idt_sw_read/write()` use the GASA address/data window under `gasa_lock` to access global switch registers. `idt_scan_ports()` derives local port/partition and fills `peers`, `port_idx_map`, and `part_idx_map`. The `idt_ntb_ops` table implements NTB callbacks: port enumeration, `link_is_up`, `link_enable/disable`, MW count/alignment/address/translation, DB masks and signals, and message status/read/write. `idt_init_pci()`, `idt_init_isr()`, `idt_register_device()`, and `idt_pci_probe()` form the probe path; `idt_pci_remove()` reverses debugfs, NTB registration, ISR, link, and PCI setup.

Control flow: Module init creates a debugfs top directory and registers `idt_pci_driver`. Probe first validates BAR0 as configuration-space mapping, allocates `idt_ntb_dev`, enables PCI/DMA/BAR resources, maps BAR0, scans switch ports, initializes link event masks, scans local and peer memory-window layouts, initializes message locks and hwmon, installs a single threaded MSI/INTx interrupt, registers the NTB device, and creates debugfs. Runtime IRQ handling reads `IDT_NT_NTINTSTS` and dispatches message, doorbell, and switch event handlers; switch events clear global event status and call `ntb_link_event()`, while DB/message handlers notify the NTB core and rely on clients to clear status bits.

State and persistence behavior: Persistent driver state lives in `struct idt_ntb_dev`: discovered port/partition/peer maps, MW descriptors, register locks, BAR0 mapping, and debugfs pointer. Hardware state is programmed in registers and persists beyond process context; link enable writes `NTCTL`, mapping-table entries, and global-signal status, while link disable clears them. The driver deliberately leaves shared switch event configuration and temperature sensor enabled on unload because the switch is shared across functions.

Dependencies and integration points: It depends on Linux PCI, NTB core, debugfs, hwmon, AER cleanup, DMA mask setup, IRQ allocation, and IDT switch register definitions from `ntb_hw_idt.h`. It integrates with NTB clients through `ntb_register_device()`, link/db/message callbacks, hwmon sysfs attributes (`temp1_input`, history, offset, reset), and debugfs diagnostics. Supported PCI IDs are generated with `IDT_PCI_DEVICE_IDS()` and per-device port-list configs.

Risks and edge cases: `idt_pci_probe()` explicitly casts away the return from `idt_scan_ports(ndev)`, so `-ENODEV` for no active peer does not stop later initialization; this can leave a zero-peer NTB device registered and makes later peer-indexed paths fragile. IDT doorbell/message IRQ semantics are level-like around shared status: if clients leave bits uncleared, unrelated events can retrigger DB/message callbacks. Global GASA, LUT, mapping table, DB mask, and message routing accesses require correct locking because register pairs are indirect. MW translation assumes BIOS/EEPROM preinitialized BAR modes and sizes; invalid or unexpected BAR setup can produce `-EINVAL` or incorrect window exposure. Debugfs message printing uses source peer index fallback to zero for unmapped source partitions, which may misrepresent unexpected sources.

Test signals: Useful validation includes probe on supported IDT hardware with multiple active NT partitions, `ntb_tool`/`ntb_pingpong` link and doorbell/message tests, MW translation tests for direct and LUT BAR modes, interrupt tests with DB and message bits left pending, hwmon sysfs read/write/clamp checks, and debugfs `info:<pci>` inspection for peer, mapping-table, MW, DB, message, and temperature state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/ntb_hw_idt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/ntb_hw_idt.h -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/ntb_hw_idt.h

Purpose: Defines the IDT NTB driver's hardware contract: PCI IDs, local NT-function and global switch register offsets, bitfield masks, helper macros, resource limits, temperature constants, and driver-private data structures.

Important APIs, types, and functions: `IDT_PCI_DEVICE_IDS()` builds PCI match entries with IDT vendor, bridge class, and model config data. The register sections cover NT config space, global switch port/partition/event/message/SMBus/temperature registers, and common fields such as `PCIELCAP_PORTNUM`, `BARSETUP_*`, `NTMTBLDATA_*`, `SWPORTxSTS_*`, and temperature fields. `GET_FIELD`, `SET_FIELD`, and `IS_FLD_SET` are central macros used by the C file for packed register fields. Core types include `enum idt_temp_val`, `enum idt_mw_type`, `struct idt_89hpes_cfg`, `struct idt_mw_cfg`, `struct idt_ntb_peer`, `struct idt_ntb_dev`, and descriptor tables for bars, messages, NT registers, ports, and partitions.

Control flow: The header has no runtime control flow, but it drives C-file control paths by encoding valid register offsets and field meanings. Port scanning depends on switch port and partition status fields; link setup depends on `NTCTL`, `NTMTBLDATA`, `SE*`, and global-signal constants; MW scanning and translation depend on `BARSETUP`, `LUTOFFSET`, and `LUTUDATA`; message routing depends on `SWPxMSGCTL`; temperature sysfs depends on `TMPSTS`, `TMPALARM`, and `TMPADJ`.

State and persistence behavior: The state layout in `struct idt_ntb_dev` captures all per-device runtime state: NTB core handle, model config, local port/partition, peer descriptors, peer lookup maps, mapping/LUT/message/doorbell/GASA locks, local BAR0 mapping, hwmon mutex, and debugfs node. Constants like `IDT_MAX_NR_PORTS`, `IDT_MAX_NR_PEERS`, and `IDT_MAX_NR_MWS` bound allocations and array scans. Hardware persistence is implied by register definitions and shared switch-global registers.

Dependencies and integration points: It includes Linux `types`, `pci`, `pci_ids`, `interrupt`, `spinlock`, `mutex`, and `ntb`. It is consumed directly by `ntb_hw_idt.c`, and its PCI ID macro is the integration point between model-specific configs and Linux PCI matching.

Risks and edge cases: The `SET_FIELD` macro does not mask the input `value` before shifting, so callers must pass bounded values. `struct idt_89hpes_cfg` uses a flexible `ports[]` member and is instantiated with static initializers in the C file, so size assumptions must remain aligned with model `port_cnt`. Many register offsets for unsupported port numbers are absent in tables rather than derivable by formula; table mistakes would cause global register access to the wrong switch state. Constants such as `IDT_DIR_SIZE_ALIGN` intentionally encode hardware quirks and can surprise generic NTB client assumptions.

Test signals: Header validation comes from compile coverage, sparse/build checks against all macro users, boot/probe on every listed IDT device ID, and register dumps comparing debugfs output with vendor documentation for BAR, partition, event, message, and temperature fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/ntb_hw_idt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/Kconfig

Purpose: Adds the `NTB_INTEL` kernel configuration option for Intel Non-Transparent Bridge hardware support.

Important APIs, types, and functions: Declares `config NTB_INTEL` as a tristate named "Intel Non-Transparent Bridge support". It depends on `X86_64` and its help text identifies capable Intel Xeon and Atom hardware.

Control flow: There is no runtime control flow. Build-time selection controls whether the Intel NTB hardware module can be built in, built as a module, or omitted.

State and persistence behavior: The chosen Kconfig value persists in the kernel `.config` and drives Makefile expansion through `CONFIG_NTB_INTEL`.

Dependencies and integration points: It integrates with the NTB hardware driver subtree and `drivers/ntb/hw/intel/Makefile`, which builds `ntb_hw_intel.o` from gen1/gen3/gen4 objects when enabled. The `X86_64` dependency prevents this hardware driver from being offered on unsupported architectures.

Risks and edge cases: There are no explicit dependencies on `PCI`, `NTB`, or `DEBUG_FS`; those are likely provided by parent menus or broader NTB infrastructure. If this Kconfig is reused outside its original tree context, missing parent dependencies could cause invalid build exposure.

Test signals: Kconfig tests include `allmodconfig`/`allyesconfig` on x86_64, checking `CONFIG_NTB_INTEL=m/y` builds the composite object, and non-x86_64 config checks showing the option is hidden.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/Makefile

Purpose: Defines the build composition for the Intel NTB hardware driver.

Important APIs, types, and functions: `obj-$(CONFIG_NTB_INTEL) += ntb_hw_intel.o` emits a single driver object when the Kconfig symbol is enabled. `ntb_hw_intel-y := ntb_hw_gen1.o ntb_hw_gen3.o ntb_hw_gen4.o` links generation-specific implementations into that object.

Control flow: Build-system flow only: Kbuild compiles the three source files and links them as the `ntb_hw_intel` module or built-in object depending on `CONFIG_NTB_INTEL`.

State and persistence behavior: No runtime state. The object list must stay synchronized with headers and PCI dispatch in `ntb_hw_gen1.c`.

Dependencies and integration points: Integrates with the surrounding kernel Kbuild system, `Kconfig`, and the shared module entry in `ntb_hw_gen1.c`, which registers one PCI driver covering gen1, gen3, gen4, gen5, and gen6 IDs.

Risks and edge cases: Adding a new generation header/source without updating this Makefile leaves PCI IDs or prototypes unresolved. Since module metadata lives in gen1, removing gen1 from the composite object would break module registration.

Test signals: `make M=drivers/ntb/hw/intel` or equivalent subtree builds should produce `ntb_hw_intel.o` and include all generation objects; link errors are the primary signal for mismatched object composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen1.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen1.c

Purpose: Provides the main Intel NTB PCI driver and common NTB operations, plus the full Gen1/Xeon implementation. It owns module metadata, PCI ID dispatch for all supported Intel generations, common ISR setup, debugfs dispatch, PCI resource setup, NTB registration, and shared helpers used by gen3/gen4.

Important APIs, types, and functions: Module parameters configure B2B MW selection/sharing and Gen1 B2B BAR addresses. Shared helpers include `ndev_mw_to_bar()`, `ndev_db_addr/read/write()`, DB mask helpers, scratchpad helpers, `ndev_init_isr()`, and `intel_ntb_*` NTB callbacks for MW, link, DB, and SPAD operations. Gen1-specific flow includes `xeon_ppd_topo()`, `xeon_setup_b2b_mw()`, `xeon_init_ntb()`, `xeon_init_dev()`, and register tables `xeon_reg`, `xeon_pri_reg`, `xeon_sec_reg`, `xeon_b2b_reg`, `xeon_pri_xlat`, and `xeon_sec_xlat`. `intel_ntb_pci_probe()` chooses gen1/gen3/gen4 paths and assigns `intel_ntb_ops`, `intel_ntb3_ops`, or `intel_ntb4_ops`.

Control flow: Probe allocates `intel_ntb_dev`, initializes default state, enables PCI resources and BAR0 mapping, calls the generation init function, resets unsafe flags, polls link once, creates debugfs, and registers with the NTB core. Gen1 init reads PPD topology, detects split BAR mode, applies errata flags by device ID, initializes MW/SPAD/DB counts and self/peer register views, sets up B2B MWs if needed, enables secondary command bits, masks doorbells, and initializes interrupts. Interrupt setup first masks DBs, tries MSI-X with per-vector handlers, then falls back to MSI and shared INTx. Runtime interrupts derive a vector mask, poll link if the link DB bit is present, and issue `ntb_link_event()`/`ntb_db_event()`.

State and persistence behavior: `intel_ntb_dev` stores topology, MW/SPAD/DB counts, B2B offsets, BAR split flag, cached DB mask, IRQ vectors, register view pointers, BAR mappings, cached link state, errata/unsafe flags, and debugfs dentries. Hardware state persists in NTB control, BAR translation/limit/base registers, doorbell masks, secondary command registers, and B2B BAR windows. Unsafe flags can be ignored via NTB unsafe callbacks and remain in-memory until device removal.

Dependencies and integration points: Depends on Linux PCI, MSI/MSI-X/INTx IRQ APIs, NTB core, debugfs, DMA mask setup, and headers `ntb_hw_intel.h`, `ntb_hw_gen1.h`, `ntb_hw_gen3.h`, and `ntb_hw_gen4.h`. Integrates all Intel generation source files into one PCI driver and exposes diagnostics through debugfs `info`.

Risks and edge cases: Hardware errata dominate the implementation: SDOORBELL/SB01BASE lockups can make DB/SPAD unsafe, B2B doorbell bit 14 may be unusable, and vector 32 can need special handling. `intel_ntb_db_vector_mask()` checks `db_vector > db_vec_count`, allowing `db_vector == db_vec_count`, which yields a mask beyond the valid vector count. Error unwind after gen3/gen4 init calls `xeon_deinit_dev()` for all generations; currently it delegates to common ISR deinit, but naming hides the cross-generation assumption. Gen1 MW translation writes and verifies hardware registers but cannot fully disable/limit primary-side windows without a visible base address. B2B module parameters must match on both hosts or peer BAR access can fail.

Test signals: Build and load with supported PCI IDs; exercise MSI-X, MSI, and INTx fallback paths; run NTB link up/down, DB, SPAD, and MW tests under primary/secondary/B2B topologies; verify errata paths on affected device IDs; inspect debugfs for topology, link, MW, DB, SPAD, and hardware error registers; run unload/reload tests to catch IRQ and BAR unmap cleanup issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen1.h -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen1.h

Purpose: Defines Gen1/Xeon Intel NTB register offsets, topology/PPD masks, resource counts, B2B address defaults, hardware errata flags, and prototypes exported from `ntb_hw_gen1.c` for reuse by gen3/gen4.

Important APIs, types, and functions: Constants cover PBAR/SBAR limits, translations, sizes, base registers, PPD, doorbells, scratchpads, link status, B2B registers, and hardware error flags. `XEON_MW_COUNT`, `HSX_SPLIT_BAR_MW_COUNT`, `XEON_DB_COUNT`, and `XEON_SPAD_COUNT` define Gen1 resource exposure. Externs `xeon_b2b_usd_addr` and `xeon_b2b_dsd_addr` provide configurable B2B translation defaults. Prototypes expose common helpers such as `ndev_init_isr()`, `xeon_ppd_topo()`, DB/SPAD helpers, MW/link callbacks, and `xeon_link_is_up()`.

Control flow: No direct runtime flow, but the constants and prototypes parameterize Gen1 init and are intentionally shared by gen3/gen4 for common NTB operations and B2B address policy.

State and persistence behavior: The header defines persistent hardware locations rather than allocating state. Errata flags are stored at runtime in `intel_ntb_dev.hwerr_flags` and interpreted by common helpers.

Dependencies and integration points: Includes `ntb_hw_intel.h`. It connects the gen1 implementation to gen3/gen4 implementations, which reuse Gen1 helper callbacks and B2B address defaults.

Risks and edge cases: The header is a shared contract beyond Gen1, so changing helper signatures or B2B constants can break gen3/gen4. BAR offset macros encode split and unsplit BAR interpretations at overlapping offsets; caller logic must select the correct one based on `bar4_split`.

Test signals: Compile coverage across gen1/gen3/gen4, Gen1 topology tests for all PPD encodings, split/non-split BAR debugfs verification, and errata-specific behavior tests are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen3.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen3.c

Purpose: Implements Intel Gen3/Skylake NTB support under the shared Intel PCI driver. It defines Gen3 register views, B2B setup, interrupt vector remapping, Gen3-specific debugfs, MW translation, and doorbell handling.

Important APIs, types, and functions: `gen3_reg`, `gen3_pri_reg`, `gen3_b2b_reg`, and `gen3_sec_xlat` describe register offsets for common helpers. `gen3_poll_link()` clears link interrupt status through `db_clear` and updates cached link status from config space. `gen3_init_isr()` rewrites interrupt vector mapping and handles the vector-32 erratum. `gen3_init_dev()` sets `gen3_reg`, reads PPD via Gen1 topology parsing, marks `NTB_HWERR_MSIX_VECTOR32_BAD`, initializes NTB state, and starts interrupts. `intel_ntb3_mw_set_trans()`, `intel_ntb3_peer_db_addr()`, `intel_ntb3_peer_db_set()`, `intel_ntb3_db_read()`, and `intel_ntb3_db_clear()` provide Gen3-specific NTB ops.

Control flow: Gen3 probe is invoked from `intel_ntb_pci_probe()` after PCI setup. It reads topology, validates B2B mode, sets two MWs, 16 SPADs, 32 DBs, link DB mask, register views, zero-length incoming limits, clears incoming translations, enables secondary memory/master command, writes the DB mask, remaps MSI-X vectors, and delegates IRQ allocation to `ndev_init_isr()`. MW translation validates default peer index, BAR-size alignment, size limits, writes IMBAR xlat/limit, verifies them, then programs endpoint EMBAR limit.

State and persistence behavior: Runtime state remains in shared `intel_ntb_dev`; Gen3 fills generation-specific register pointers and cached masks. Hardware state is persisted in IMBAR/EMBAR xlat/limit registers, interrupt vector table, interrupt disable/status registers, and secondary command register. Doorbell writes are per-bit 32-bit writes into spaced doorbell registers rather than one packed write.

Dependencies and integration points: Depends on common helpers from `ntb_hw_gen1.c`, shared structs from `ntb_hw_intel.h`, and constants/prototypes from `ntb_hw_gen3.h`. Its `intel_ntb3_ops` is selected by the main Intel PCI driver for SKX PCI IDs.

Risks and edge cases: The vector-32 workaround removes link bits from `db_valid_mask`, so DB tests must account for a reduced usable mask. `gen3_setup_b2b_mw()` leaves `peer_mmio` equal to `self_mmio`, so peer register offsets must be correct for the B2B window model. MW translation assumes BAR-size address alignment and verifies register writes, returning `-EIO` on mismatch. Only B2B topology is accepted; unexpected PPD values fail probe.

Test signals: Hardware or emulation tests should cover SKX B2B probe, MSI-X vector remapping, link event delivery, DB per-bit writes/clears, MW translation with valid and invalid alignment/size, debugfs Gen3 xlat/error output, and unload cleanup through the shared deinit path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen3.h -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen3.h

Purpose: Provides Intel Skylake/Gen3 NTB register offsets, resource counts, inline 64-bit doorbell accessors, and exported Gen3 function prototypes.

Important APIs, types, and functions: Defines Gen3 PCI config offsets for BAR sizes and error/link status, BAR0 MMIO offsets for NTB control, IM/EM BAR xlat/limits, interrupt status/masks, interrupt vectors, SPADs, doorbells, B2B SPADs, and secondary command/BARs. `GEN3_DB_COUNT`, `GEN3_DB_LINK`, vector constants, and `GEN3_SPAD_COUNT` describe resources. `gen3_db_ioread()`/`gen3_db_iowrite()` provide 64-bit DB access wrappers. Externs declare debugfs, init, link, DB, peer DB, and `intel_ntb3_ops`.

Control flow: No direct flow, but the offsets drive Gen3 init, debugfs, interrupts, DB operations, and MW translation in `ntb_hw_gen3.c`.

State and persistence behavior: Hardware state addressed by this header persists in Gen3 MMIO/config registers; runtime state is stored in `intel_ntb_dev` via shared register descriptor structures.

Dependencies and integration points: Includes `ntb_hw_intel.h` and is consumed by the main Gen1 file and Gen3 implementation. The main Intel driver references `intel_ntb3_ops` and `gen3_init_dev()` through this header.

Risks and edge cases: Doorbell register size is represented as `sizeof(u32)` in the Gen3 reg table while accessors read/write 64-bit masks; this matches the logical DB mask implementation but deserves hardware regression coverage. Offsets for IM and EM spaces are separated by `0x4000`; incorrect descriptor selection would target the wrong side.

Test signals: Compile checks, debugfs register sanity on SKX hardware, DB mask/vector tests, and MW xlat/limit register readback tests are the best validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen4.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen4.c

Purpose: Implements Intel Gen4/Gen5/Gen6 NTB support for ICX, later SPR-class Gen4 revisions, GNR, and DMR devices under the shared Intel NTB PCI driver.

Important APIs, types, and functions: `gen4_reg`, `gen4_pri_reg`, `gen4_b2b_reg`, and `gen4_sec_xlat` define register views. `get_ppd0()` selects the proper PPD0 offset for Gen4/5/6. `gen4_poll_link()` clears slot DLL status and DB interrupt status, then updates cached link status from MMIO. `gen4_init_dev()` sets errata flags for ICX, decodes topology from PPD1, initializes B2B NTB state, disables link initially, and initializes IRQs. `intel_ntb4_mw_set_trans()` programs xlat/limit and optional base-index registers; `intel_ntb4_link_enable()` programs LTR, snoop control, link control, and PPD link-training; `intel_ntb4_link_disable()` reverses snoop/link state and selects idle LTR; `intel_ntb4_mw_get_align()` reports BAR-size or page alignment depending on errata.

Control flow: Main probe dispatch calls `gen4_init_dev()` after PCI setup. Gen4 init reads topology, sets register views and resources, sets zero-length incoming limits, clears incoming translations, masks doorbells, disables the link, then remaps vectors and allocates IRQs. Link enable ignores requested speed/width, optionally programs active/idle LTR values, sets E2I/I2E snoop bits, clears link-disable, sets PPD link-training, verifies the training bit, and marks `dev_up`.

State and persistence behavior: Shared `intel_ntb_dev` holds cached link status, topology, resource counts, generation register pointers, DB masks, and `dev_up`. Hardware state persists in GEN4 NTB control, link control/status, PPD link-training, LTR registers, IM xlat/limit/base-index, doorbell mask/status, and interrupt vector registers.

Dependencies and integration points: Depends on `linux/log2.h` for `__ilog2_u64`, common Intel helpers, and Gen3 DB helpers/ops for DB semantics. `intel_ntb4_ops` is selected by the main PCI driver for ICX, GNR, and DMR IDs, and reuses Gen3 DB read/clear/peer DB methods plus common SPAD callbacks.

Risks and edge cases: ICX sets `NTB_HWERR_BAR_ALIGN` and `NTB_HWERR_LTR_BAD`, forcing BAR-size alignment and skipping LTR programming; later devices permit page alignment. `get_ppd0()` returns `ULLONG_MAX` for unexpected devices, so callers rely on earlier generation checks. `intel_ntb4_link_enable()` verifies only that the PPD training bit latched, not that the link actually becomes active. `intel_ntb4_mw_set_trans()` computes base index from `size`/`mw_size`; non-power-of-two sizes would be rounded by `__ilog2_u64` if callers pass them despite size_align being 1.

Test signals: Validate ICX and SPR/GNR/DMR topology decoding, link enable/disable transitions, LTR programming/skipping, MW translation alignment differences, base-index readback on ICX, vector remap and link interrupt delivery, Gen3-style DB operations, and debugfs output for cached and live link/error registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen4.h -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen4.h

Purpose: Defines Intel Gen4 through Gen6 NTB register offsets, topology masks, resource counts, link/LTR control bits, revision helpers, and exported Gen4 APIs.

Important APIs, types, and functions: Constants cover ICX revision range, Gen4 BAR-size config offsets, MMIO NTB control, xlat/limit/index, interrupt status/masks/vectors, SPADs, doorbells, LTR registers, link control/status, PPD0/PPD1, slot status, topology masks for ICX and SPR-like devices, DB/SPAD counts, snoop/nosnoop control bits, link-down and force-detect bits, LTR values, and Gen6 PPD0 offset. Prototypes declare `ndev_ntb4_debugfs_read()`, `gen4_init_dev()`, and `intel_ntb4_ops`. Inline helpers `pdev_is_ICX()` and `pdev_is_SPR()` classify Gen4 revisions.

Control flow: The header itself has no flow; its revision helpers and constants drive Gen4 init, link enable/disable, MW setup, and debugfs in `ntb_hw_gen4.c`.

State and persistence behavior: Hardware state addressed here persists in Gen4+ MMIO/config registers. Runtime state is held in shared `intel_ntb_dev`, including the Gen4-only `dev_up` field declared in `ntb_hw_intel.h`.

Dependencies and integration points: Includes `ntb_hw_intel.h` and is included by the main Intel file and Gen4 implementation. It bridges PCI ID generation helpers from `ntb_hw_intel.h` to revision-specific ICX/SPR behavior.

Risks and edge cases: The header has duplicate declarations for `ndev_ntb4_debugfs_read()`. `NTB_CTL_E2I_BAR45_NOSNOO` appears to be missing the final `P` in the macro name, which can trip future users even though current code does not use that macro. Revision-based `pdev_is_SPR()` treats any Gen4 revision above ICX max as SPR-like, so future Gen4 revisions inherit SPR topology parsing unless split out.

Test signals: Compile coverage, Gen4 revision matrix tests, static checks for unused/misspelled macros, and hardware readback of link/LTR/xlat/vector offsets validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_intel.h -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_intel.h

Purpose: Defines shared Intel NTB device IDs, common NTB control/link macros, unsafe-access flags, BAR masks, common register descriptor structs, the central `intel_ntb_dev` runtime state, and PCI generation classifier helpers.

Important APIs, types, and functions: Device ID macros cover Gen1 JSF/SNB/IVT/HSX/BDX primary/secondary/B2B IDs, Gen3 SKX, Gen4 ICX, Gen5 GNR, and Gen6 DMR. `NTB_CTL_*` and `NTB_LNK_STA_*` abstract common control and link status bits. `struct intel_ntb_reg`, `intel_ntb_alt_reg`, and `intel_ntb_xlat_reg` describe generation-specific register layouts consumed by common code. `struct intel_b2b_addr` stores B2B BAR translation defaults. `struct intel_ntb_vec` and `struct intel_ntb_dev` hold IRQ and per-device state. Inline helpers classify PCI devices by generation.

Control flow: No direct flow, but all Intel C files use `intel_ntb_dev` and classifier helpers to choose generation init paths and NTB ops.

State and persistence behavior: `intel_ntb_dev` is the central in-memory state for the Intel driver: NTB core handle, B2B placement, BAR split flag, cached NTB control/link state, resource counts, DB masks, IRQ vector arrays, register layout pointers, self/peer MMIO mappings, peer physical address, heartbeat timestamp/work, errata/unsafe flags, debugfs state, and Gen4 `dev_up`.

Dependencies and integration points: Includes Linux NTB, PCI, and non-atomic lo/hi 64-bit I/O support. It is shared by gen1/gen3/gen4 headers and implementations. The PCI classifier helpers integrate with the main probe logic and debugfs dispatch.

Risks and edge cases: The generation classifier helpers are hardcoded switch/if lists, so new PCI IDs must be added both here and in the PCI ID table. `intel_ntb_reg` uses a flexible `mw_bar[]` member and is instantiated with static trailing initializers; any access depends on correct `mw_count`. `db_size` sometimes represents register stride/size imperfectly for newer hardware, so users should rely on generation DB helpers.

Test signals: Full Intel driver build, probe dispatch for every PCI ID, classifier unit-style checks if available, and debugfs/register sanity tests across generations validate this shared contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/Kconfig

Purpose: Adds the MicroSemi Switchtec NTB hardware driver configuration option.

Important APIs, types, and functions: Declares `config NTB_SWITCHTEC` as a tristate named "MicroSemi Switchtec Non-Transparent Bridge Support". It selects `PCI_SW_SWITCHTEC` because the NTB driver shares hardware interface access with the Switchtec management driver.

Control flow: Build-time only. Selecting the symbol enables the Switchtec NTB object through the MSCC Makefile and pulls in the management driver dependency.

State and persistence behavior: The Kconfig value persists in kernel configuration and controls whether `ntb_hw_switchtec.o` is built.

Dependencies and integration points: Integrates with the Switchtec PCI switch management subsystem via `select PCI_SW_SWITCHTEC` and with the NTB hardware subtree through the local Makefile.

Risks and edge cases: `select` forces `PCI_SW_SWITCHTEC` without exposing a prompt dependency here, so dependency correctness relies on the selected symbol's own constraints. Misconfiguration can affect both NTB and management-driver interfaces because they share hardware access.

Test signals: Kconfig `m/y/n` builds, verifying `PCI_SW_SWITCHTEC` is selected, and module load testing with Switchtec hardware are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/Makefile

Purpose: Defines the Kbuild rule for the MicroSemi Switchtec NTB hardware driver.

Important APIs, types, and functions: `obj-$(CONFIG_NTB_SWITCHTEC) += ntb_hw_switchtec.o` compiles and links the Switchtec NTB driver when the Kconfig option is enabled.

Control flow: Build-system only; no runtime logic.

State and persistence behavior: No runtime state. The build artifact presence follows the persistent kernel `.config`.

Dependencies and integration points: Connects `CONFIG_NTB_SWITCHTEC` from MSCC Kconfig to the Switchtec NTB implementation source elsewhere in the same directory/subtree.

Risks and edge cases: If the implementation object is renamed or split, this Makefile must be updated. Because Kconfig selects the Switchtec management driver, build failures may surface in either NTB or management-driver dependencies.

Test signals: Subtree build with `CONFIG_NTB_SWITCHTEC=m/y` should emit `ntb_hw_switchtec.o`; disabled configs should omit it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/Makefile -->
