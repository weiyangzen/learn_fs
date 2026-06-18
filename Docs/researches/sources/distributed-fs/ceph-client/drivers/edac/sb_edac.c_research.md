# sources/distributed-fs/ceph-client/drivers/edac/sb_edac.c

## Purpose
Implements EDAC memory-controller support for Intel Sandy Bridge-EP, Ivy Bridge-EP, Haswell-EP, Broadwell-EP/D, and Knights Landing/Knights Mill server platforms. It discovers the many PCI functions that expose IMC/SAD/TAD/RIR registers, builds EDAC DIMM topology, decodes memory machine-check events, and reports corrected, uncorrected, or fatal memory errors.

## Important APIs, Types, And Functions
- `struct sbridge_info`, `struct sbridge_dev`, `struct sbridge_pvt`, and `struct knl_pvt` model generation-specific callbacks, PCI devices, EDAC-private topology, and KNL-specific device arrays.
- PCI ID descriptor tables define the required and optional PCI functions for each CPU generation.
- `sbridge_get_all_devices`, `sbridge_get_onedevice`, and bind helpers collect PCI devices and attach them to the private structure.
- `get_dimm_config`, `__populate_dimms`, and `knl_get_dimm_capacity` fill EDAC DIMM sizes, labels, memory type, width, rank, row/column, mirroring, lockstep, and page-mode state.
- `get_memory_layout` logs TOLM/TOHM, SAD, TAD, offsets, and RIR layout.
- `get_memory_error_data` decodes a physical address through SAD, TAD, channel, RIR, and Broadwell row/column logic.
- `get_memory_error_data_from_mce` uses MCE-provided channel data when the address granularity is too coarse.
- `sbridge_mce_check_error` and `sbridge_mce_output_error` filter MCEs, classify severity, decode location, and call `edac_mc_handle_error`.
- `sbridge_register_mci`, `sbridge_probe`, `sbridge_init`, and `sbridge_exit` manage EDAC and MCE notifier lifetime.

## Control Flow
Module init rejects GHES ownership, other EDAC owners, hypervisors, and unsupported CPU models, then initializes EDAC opstate and probes the generation's PCI table. Probe gathers all required PCI functions, creates one EDAC MC per discovered IMC/domain, binds generation-specific devices, fills `sbridge_info` callbacks, obtains source/node IDs, reads DIMM and memory-layout state, and registers each MC. When an MCE arrives, the notifier filters non-memory errors, missing address/misc validity, and non-physical-address reports. Output classification derives CE/UE/fatal, handles KNL specially, otherwise decodes by physical address or MCE channel bits, adjusts for mirroring/lockstep/channel masks, and reports the event.

## State And Persistence
Global state includes `sbridge_edac_list` and static message buffers. Each `sbridge_dev` owns PCI device references and the associated `mem_ctl_info`; each `sbridge_pvt` caches PCI function pointers, generation callbacks, channel/DIMM metadata, memory limits, mirroring/lockstep state, and KNL route devices. Hardware topology is read at probe and used for all later MCE decodes. Exit unregisters MCs, releases PCI references, and unregisters the MCE notifier.

## Dependencies And Integration Points
Depends on x86 CPU model matching, PCI config space, Intel machine-check records, EDAC MC APIs, GHES/EDAC ownership arbitration, and generation-specific Intel IMC register layouts. It integrates with the MCE decode chain at `MCE_PRIO_EDAC` and marks handled records with `MCE_HANDLED_EDAC`.

## Risks And Edge Cases
The decode logic is highly generation-specific and includes documented FIXME areas for channel index offsets, lockstep row/column decode, DDR3 row/column decode, and channel-mask support in EDAC reporting. KNL capacity is inferred from SAD/TAD/route tables and can underreport if BIOS maps less than installed memory. PCI discovery must balance references across optional, shared, duplicated, and multi-bus devices. Static message buffers are shared by notifier execution. Mirroring and lockstep can make a single-DIMM report ambiguous.

## Test Signals
Use per-generation PCI discovery tests, missing optional/required device paths, ECC-disabled DIMM rejection, TOLM/TOHM/SAD/TAD/RIR layout dumps, MCE filtering for ADDRV/MISCV/address type, address decodes across SAD/TAD/RIR boundaries, Haswell/Broadwell channel hashing and mirroring, Broadwell DDR4 row/column decode, KNL EDRAM and DRAM channel reports, and notifier cleanup on unload.
