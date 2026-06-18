# sources/distributed-fs/ceph-client/drivers/edac/highbank_mc_edac.c

## Purpose
This platform EDAC memory-controller driver reports Calxeda Highbank and Midway DDR ECC events. It maps controller ECC/error interrupt registers, registers one logical DIMM, handles CE/UE IRQs, and exposes a sysfs injection control.

## Important APIs and Functions
`struct hb_mc_drvdata` stores error and interrupt register bases. `highbank_mc_err_handler()` reads interrupt status, decodes UE/CE address and syndrome, reports through `edac_mc_handle_error()`, and acknowledges interrupts. `highbank_mc_err_inject()` and `highbank_mc_inject_ctrl()` configure ECC syndrome injection. `hb_mc_settings` selects register offsets for Highbank versus ECX-2000/Midway variants. `highbank_mc_probe()` and `highbank_mc_remove()` manage platform lifecycle.

## Control Flow
Probe matches the DT compatible string, allocates a chip-select/channel EDAC controller, maps the MMIO resource, computes error and interrupt sub-bases from match data, verifies ECC mode, fills EDAC capabilities and a single 4GB DDR3 DIMM, registers sysfs groups, then requests the IRQ. IRQ handling reports uncorrectable errors first, then correctable errors, then writes the observed status to the ACK register.

## State and Persistence
Runtime state is the mapped register sub-bases and EDAC DIMM/controller metadata. Injection writes change controller ECC option bits. No state is persisted outside hardware registers and EDAC sysfs counters.

## Dependencies and Integration
The driver depends on Open Firmware matching, platform resources/IRQs, EDAC memory-controller APIs, and sysfs attribute groups. It integrates corrected/uncorrected DDR events into standard EDAC counters.

## Risks
The model hard-codes a single 4GB DIMM, which may not describe all physical configurations precisely. The IRQ handler does not explicitly test for zero status before returning handled. Injection is writable by root and directly alters ECC option bits, so test environments must isolate it.

## Test Signals
Expected signals are successful probe only when ECC mode is active, EDAC DIMM metadata for DDR3 SECDED, CE/UE reports with PFN/offset/syndrome from registers, ACK writes matching interrupt status, and working `inject_ctrl` sysfs writes.
