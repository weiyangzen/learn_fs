# sources/distributed-fs/ceph-client/drivers/edac/i7core_edac.c Research

## Purpose
`i7core_edac.c` supports Intel Nehalem, Lynnfield, Westmere, Xeon 35xx/55xx/56xx, i7/i5 memory controllers. It discovers per-socket non-core and memory-controller PCI functions, registers EDAC memory controllers, decodes DDR3 DIMM geometry, handles memory-controller MCE bank 8 notifications, maintains corrected-error counters, exposes error-injection sysfs controls, and optionally controls hardware patrol scrub rate.

## Important APIs, Types, and Functions
`struct i7core_dev` groups all PCI functions for one socket and links into `i7core_edac_list`. `struct i7core_pvt` binds those PCI functions to one EDAC controller and holds DIMM topology, injection settings, corrected-error counters, scrub state, DCLK frequency, and a generic PCI EDAC control object. PCI discovery is table-driven through `struct pci_id_descr`, `struct pci_id_table`, `i7core_get_all_devices()`, and `mci_bind_devs()`.

`get_dimm_config()` reads MC_CONTROL, MC_STATUS, MC_MAX_DOD, channel mapper, per-channel DIMM init, and DOD registers to populate EDAC DIMM geometry, type (`MEM_DDR3` or `MEM_RDDR3`), x4/x8/x16 device width, labels, grain, and EDAC mode. `i7core_mce_check_error()` filters MCEs to memory-controller bank 8 and socket-local controllers. `i7core_mce_output_error()` decodes operation, syndrome, DIMM, channel, corrected/uncorrected/fatal status and reports via `edac_mc_handle_error()`. `i7core_udimm_check_mc_ecc_err()` and `i7core_rdimm_check_mc_ecc_err()` read corrected-error counters and account wraparound.

The sysfs injection path uses `inject_section`, `inject_type`, `inject_eccmask`, `inject_enable`, and `inject_addrmatch/*` attributes. `i7core_inject_enable_store()` builds address-match and injection masks, unlocks PCI config writes, programs channel error injection registers, and toggles an undocumented non-core control value. Scrub support uses `set_sdram_scrub_rate()` and `get_sdram_scrub_rate()` when the platform exposes RAS function 2.

## Control Flow
Module init initializes EDAC opstate, optionally scans hidden Xeon buses, registers a PCI driver, and registers an MCE decode notifier. The first PCI probe claims all socket devices, allocates one EDAC controller per discovered socket, binds PCI functions, reads DIMM config, enables scrub hooks if available, registers EDAC with attribute groups, creates auxiliary sysfs devices, creates generic PCI EDAC control, and records DCLK from DMI.

Runtime MCE notification looks up the socket, rejects non-memory and non-bank-8 events, reports the MCE, updates CE counters, and marks the MCE handled. Removal unregisters all controllers, releases sysfs devices, releases generic PCI control, disables scrub programming, frees controller names and MC objects, and drops all PCI references.

## State and Persistence
State is entirely in kernel memory, PCI config registers, EDAC sysfs devices, MCE notifier registration, and optional hardware scrub/injection registers. Corrected-error totals persist only while the module is loaded. Injection settings are writable sysfs state and are disabled when parameters change.

## Dependencies and Integration Points
The driver depends on PCI enumeration, DMI walking, EDAC MC and PCI control, Linux MCE notifier APIs, `edac_module.h`, and Intel PCI IDs. It shares the global x86 MCE path with other EDAC decoders and coordinates with `MCE_HANDLED_CEC`/`MCE_HANDLED_EDAC`.

## Risks and Edge Cases
PCI discovery is fragile because hidden non-core buses may require `use_pci_fixup` scanning. Socket numbering derives from bus order. Error injection is privileged and can create real memory errors; mask construction is sensitive to DIMM count and channel selection. Corrected-error counters are 15-bit hardware counters with wraparound. MCE decoding intentionally ignores non-bank-8 or non-memory errors, and RDIMM corrected errors are counted through polling-style registers rather than direct MCE payloads.

## Test Signals
Test with supported Nehalem/Westmere systems should verify all socket PCI functions are claimed, DIMM sysfs geometry matches hardware, MCE bank 8 memory errors are reported once, CE counters increase under injected or scrubbed corrected errors, sysfs injection knobs program and disable registers, scrub rate set/get round-trips, and unload removes auxiliary sysfs devices without leaks.
