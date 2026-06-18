# sources/distributed-fs/ceph-client/drivers/edac/igen6_edac.c Research

## Purpose
`igen6_edac.c` is the EDAC driver for Intel client SoCs with In-Band ECC (IBECC). It detects IBECC-capable PCI host bridges, maps MCHBAR/IMC/IBECC register windows, builds EDAC DIMM topology, decodes IBECC error-log addresses into system/channel/DIMM locations, and handles error notification through polling, SERR NMI, or MCE depending on the SoC generation.

## Important APIs, Types, and Functions
`struct res_config` captures per-generation behavior: machine-check mode, number of IMCs, MCHBAR/TOM masks, ECC log masks, IMC/CMF/IBECC offsets, availability callbacks, optional custom error-address extraction, and address conversion callbacks. Config instances cover EHL, ICL, TGL, ADL/ADL-N/AZB/ASL, RPL-P, Meteor/Arrow/Panther/Wildcat variants. `struct igen6_imc` holds one controller's EDAC MC, PCI device, unique device object, mapped window, channel and DIMM decode sizes/maps. `struct igen6_pvt` holds all IMCs plus memory-slice hash state.

`igen6_pci_setup()` checks IBECC availability, reads TOLUD/TOM/MCHBAR, and initializes global memory bounds. Address translation helpers handle generation differences: EHL low/high hole adjustments, TGL memory-slice hashing, ADL IMC address extraction, and RPL-P ECC-log address masks. `igen6_get_dimm_config()` reads MAD_INTER/MAD_INTRA/MAD_DIMM registers, verifies IBECC activation, and fills DIMM size/type/width/grain/SECDED metadata. `igen6_decode()` decodes channel and sub-channel using hash registers. `igen6_output_error()` reports to EDAC with syndrome and decoded channel/sub-channel.

The error path uses `ecclog_read_and_clear()`, `ecclog_gen_pool_add()`, a lockless `llist`, `irq_work`, and a workqueue. This lets NMI/MCE context snapshot and queue ECC logs while the worker performs printk and EDAC reporting. Debug builds expose `igen6_test/addr` to inject a fake corrected log.

## Control Flow
Probe allocates global state, selects the generation config, validates PCI/MCHBAR, sets EDAC opstate, maps and registers present IMCs, reads memory-slice hash state when needed, creates the NMI-safe pool, initializes work items, registers the proper error handler, enables PCI error reporting, drains pending logs, and sets up debugfs. Polling calls `igen6_check()` per MC. NMI/MCE handlers call `ecclog_handler()` and schedule deferred processing. Remove disables debugfs and reporting, unregisters handlers, synchronizes irq_work/workqueue, destroys the pool, unregisters MCs, unmaps windows, and frees global state.

## State and Persistence
State lives in mapped MMIO, EDAC MC objects, global `res_cfg`/`igen6_pvt`, global TOLUD/TOM, the ECC log gen_pool, lockless list, irq_work/workqueue, and optional debugfs. Error log registers are cleared by write-one-to-clear. No disk persistence is used.

## Dependencies and Integration Points
The driver depends on PCI, EDAC MC/debugfs helpers, x86 MCE and NMI APIs, `genalloc`, lockless lists, irq_work, and GHES/EDAC owner arbitration. It refuses to load when GHES owns error reporting or another EDAC owner is active.

## Risks and Edge Cases
NMI safety is central: allocation uses a prebuilt gen_pool and heavy work is deferred. Pool exhaustion drops detailed reporting for some logs. Address translation is generation-specific and sensitive to hash register semantics. `errcmd_enable_error_reporting()` uses `ERRSTS_UE` in the mask path, which is numerically aligned but semantically surprising. Some SoCs force polling because interrupts are unreliable. Invalid ECC logs of all ones are explicitly skipped to avoid floods.

## Test Signals
Test with supported PCI IDs should verify IBECC availability gating, MCHBAR and IMC absent detection, DIMM geometry and ECC-active checks, polling/NMI/MCE paths, correct decoding of multi-IMC and memory-slice interleaves, debugfs fake error reporting under `CONFIG_EDAC_DEBUG`, clean synchronization on remove, and no reports when GHES owns EDAC.
