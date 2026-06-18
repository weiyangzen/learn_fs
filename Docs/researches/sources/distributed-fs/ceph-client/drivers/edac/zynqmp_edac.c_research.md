# sources/distributed-fs/ceph-client/drivers/edac/zynqmp_edac.c

## Purpose
`zynqmp_edac.c` implements EDAC-device support for Xilinx/AMD ZynqMP OCM ECC. It reports correctable and uncorrectable ECC events from OCM interrupt/status registers and optionally provides debugfs fault-injection controls.

## Important APIs, types, and functions
State lives in `struct edac_priv`, which stores the OCM MMIO base, EDAC message buffer, counters, current `struct ecc_status`, and debugfs injection fields. `get_error_info()` reads CE/UE fault address and data registers and clears the interrupt source. `handle_error()` formats EDAC messages and calls `edac_device_handle_ce()` or `edac_device_handle_ue()`. `intr_handler()` is the IRQ entry point. `edac_probe()` and `edac_remove()` own platform lifecycle. Debug builds add `inject_ce_write()`, `inject_ue_write()`, `write_fault_count()`, and `setup_debugfs()`.

## Control flow
Probe maps the OCM resource, refuses to bind if ECC is disabled in `ECC_CTRL_OFST`, allocates one EDAC device instance, requests the platform IRQ, enables CE/UE interrupts through `OCM_IEN_OFST`, creates debugfs entries when available, and registers the EDAC device. The IRQ handler reads `OCM_ISR_OFST`, ignores unrelated interrupts, collects either CE or UE details, increments total counters, reports through EDAC, and clears transient status. Removal disables CE/UE interrupts, removes debugfs, unregisters, and frees EDAC state.

## State and persistence behavior
The driver keeps runtime counters (`ce_cnt`, `ue_cnt`) and the last in-flight status in memory. Hardware keeps first-failing address/data registers until the handler clears CE/UE bits. Debugfs fault bit positions and fault count are stored in memory and written to OCM injection registers. There is no persistent storage.

## Dependencies and integration points
It depends on platform devices, OF match `xlnx,zynqmp-ocmc-1.0`, EDAC device APIs, MMIO, IRQs, and optional EDAC debugfs. It integrates with user diagnostics through EDAC logs/counters and debugfs injection files `inject_fault_count`, `inject_ue_bitpos`, and `inject_ce_bitpos`.

## Risks and edge cases
`get_error_info()` uses `if/else if`, so simultaneous CE and UE bits are handled one class per interrupt invocation. The UE debug path copies into `char buf[6]` and then writes `buf[len] = '\0'`; a full-size copy can index one byte past the array. Injection bit parsing must reject duplicate UE bit positions and bit positions above 63. Probe returns `-ENXIO` when firmware has not enabled ECC, so platform setup is a hard dependency.

## Test signals
Exercise probe with ECC enabled/disabled, CE and UE interrupts, interrupt clear behavior, debugfs CE/UE injection including invalid/duplicate bits and oversized counts, suspend/resume wake behavior through generic IRQ state, remove cleanup, and fault injection for IRQ request or EDAC registration failures.
