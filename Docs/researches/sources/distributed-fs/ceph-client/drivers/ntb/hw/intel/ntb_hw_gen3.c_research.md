# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen3.c

Purpose: Implements Intel Gen3/Skylake NTB support under the shared Intel PCI driver. It defines Gen3 register views, B2B setup, interrupt vector remapping, Gen3-specific debugfs, MW translation, and doorbell handling.

Important APIs, types, and functions: `gen3_reg`, `gen3_pri_reg`, `gen3_b2b_reg`, and `gen3_sec_xlat` describe register offsets for common helpers. `gen3_poll_link()` clears link interrupt status through `db_clear` and updates cached link status from config space. `gen3_init_isr()` rewrites interrupt vector mapping and handles the vector-32 erratum. `gen3_init_dev()` sets `gen3_reg`, reads PPD via Gen1 topology parsing, marks `NTB_HWERR_MSIX_VECTOR32_BAD`, initializes NTB state, and starts interrupts. `intel_ntb3_mw_set_trans()`, `intel_ntb3_peer_db_addr()`, `intel_ntb3_peer_db_set()`, `intel_ntb3_db_read()`, and `intel_ntb3_db_clear()` provide Gen3-specific NTB ops.

Control flow: Gen3 probe is invoked from `intel_ntb_pci_probe()` after PCI setup. It reads topology, validates B2B mode, sets two MWs, 16 SPADs, 32 DBs, link DB mask, register views, zero-length incoming limits, clears incoming translations, enables secondary memory/master command, writes the DB mask, remaps MSI-X vectors, and delegates IRQ allocation to `ndev_init_isr()`. MW translation validates default peer index, BAR-size alignment, size limits, writes IMBAR xlat/limit, verifies them, then programs endpoint EMBAR limit.

State and persistence behavior: Runtime state remains in shared `intel_ntb_dev`; Gen3 fills generation-specific register pointers and cached masks. Hardware state is persisted in IMBAR/EMBAR xlat/limit registers, interrupt vector table, interrupt disable/status registers, and secondary command register. Doorbell writes are per-bit 32-bit writes into spaced doorbell registers rather than one packed write.

Dependencies and integration points: Depends on common helpers from `ntb_hw_gen1.c`, shared structs from `ntb_hw_intel.h`, and constants/prototypes from `ntb_hw_gen3.h`. Its `intel_ntb3_ops` is selected by the main Intel PCI driver for SKX PCI IDs.

Risks and edge cases: The vector-32 workaround removes link bits from `db_valid_mask`, so DB tests must account for a reduced usable mask. `gen3_setup_b2b_mw()` leaves `peer_mmio` equal to `self_mmio`, so peer register offsets must be correct for the B2B window model. MW translation assumes BAR-size address alignment and verifies register writes, returning `-EIO` on mismatch. Only B2B topology is accepted; unexpected PPD values fail probe.

Test signals: Hardware or emulation tests should cover SKX B2B probe, MSI-X vector remapping, link event delivery, DB per-bit writes/clears, MW translation with valid and invalid alignment/size, debugfs Gen3 xlat/error output, and unload cleanup through the shared deinit path.
