# sources/distributed-fs/ceph-client/drivers/edac/i7300_edac.c Research

## Purpose
`i7300_edac.c` is the EDAC memory-controller driver for Intel 7300/Clarksboro chipsets with FB-DIMM memory. It discovers the multi-function MCH PCI topology, enumerates branches/channels/slots, decodes Memory Technology Registers into EDAC DIMM metadata, enables FB-DIMM error reporting, and polls global and FBD error registers to report fatal, uncorrectable, and correctable memory events.

## Important APIs, Types, and Functions
The main private state is `struct i7300_pvt`, which caches the required PCI functions, branch devices, controller settings, MIR/MTR/AMB-present registers, per-slot/channel size data, and a temporary print buffer. `i7300_get_devices()` finds device 16 functions 1 and 2 plus branch devices 21.0 and 22.0; `i7300_put_devices()` drops those references. `i7300_get_mc_regs()` reads AMBASE, TOLM, MC settings, MIR registers, and then calls `i7300_init_csrows()`.

`decode_mtr()` is the central DIMM decoder. It turns MTR bank/row/column/rank/width fields into DIMM size, memory type `MEM_FB_DDR2`, device width, and EDAC mode. Single mode uses SECDED; normal/mirrored lockstep uses S4ECD4ED or S8ECD8ED depending on x4/x8 DRAM. `i7300_process_error_global()` reports global MCH/FSB/PCIe/FBD fatal and non-fatal registers to the kernel log, while `i7300_process_fbd_error()` reads FERR_FAT_FBD/FERR_NF_FBD plus NRECMEM/RECMEM/REDMEM detail registers and reports through `edac_mc_handle_error()`. `i7300_enable_error_reporting()` unmasks FBD errors in `EMASK_FBD`.

## Control Flow
Module init calls `opstate_init()` and registers a PCI driver for the I7300 MCH error device. Probe accepts only function 0, allocates a three-layer EDAC topology of branch, channel, and slot, allocates a page-sized message buffer, gathers companion PCI devices, populates `mem_ctl_info`, decodes memory configuration, optionally enables reporting, registers with EDAC, clears stale errors, and creates generic PCI EDAC control.

During polling, `i7300_check_error()` checks global errors first and then FB-DIMM errors. Fatal FB-DIMM errors use non-recoverable memory address detail registers and are reported as `HW_EVENT_ERR_FATAL`; non-fatal FB-DIMM errors read syndrome/channel/detail registers and are currently reported as corrected errors. Remove releases generic PCI control, unregisters the EDAC MC, drops companion PCI device references, frees the temporary buffer, and frees the MC object.

## State and Persistence
There is no filesystem persistence. Runtime state lives in PCI config registers, `struct mem_ctl_info`, `struct i7300_pvt`, EDAC core registration, and the global `i7300_pci` pointer. Hardware error registers are read-clear/write-one-to-clear; driver-cached MTR/MIR/AMB settings are probe-time snapshots.

## Dependencies and Integration Points
The driver depends on Linux PCI APIs, EDAC MC APIs, generic EDAC PCI control, `edac_module.h`, and Intel PCI IDs for the I7300 MCH/FBD functions. It integrates with EDAC polling/NMI state through the global `edac_op_state` module parameter.

## Risks and Edge Cases
Companion PCI functions are mandatory; hidden or broken BIOS enumeration makes probe fail. Error detail reads are not atomic, so only first set bits are decoded and concurrent errors can be compressed into one report. The corrected-error location uses `branch >> 1`, which makes branch information coarse, and physical page/offset details are not reconstructed for FBD reports. DIMM presence relies on MTR fields rather than AMB-present fields because AMB register semantics are ambiguous.

## Test Signals
Useful signals include successful probe on I7300 hardware, EDAC sysfs DIMM layout matching physical FB-DIMMs, EMASK_FBD becoming unmasked, poll-time reports for FERR_GLOBAL and FERR_FBD injections, clean module unload with no leaked PCI references, and dmesg debug output for MIR/MTR/AMB decoding under `CONFIG_EDAC_DEBUG`.
