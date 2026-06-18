# sources/distributed-fs/ceph-client/drivers/edac/al_mc_edac.c Research

## Purpose
This platform driver reports ECC errors from Amazon Annapurna Labs Alpine memory controllers. It supports correctable and uncorrectable DRAM ECC events, reporting syndrome/address fields through the EDAC memory-controller framework using either interrupts or polling.

## Important APIs, Types, and Functions
`struct al_mc_edac` stores the MMIO base, spinlock, and CE/UE IRQ numbers. Register definitions cover ECC config, clear, count, CE/UE address, and syndrome registers. `prepare_msg()` formats rank/row/bank-group/bank/column/syndrome details. `handle_ce()` and `handle_ue()` read count/address/syndrome registers, clear status bits, and call `edac_mc_handle_error()`. `al_mc_edac_check()` is the polling hook for missing IRQs. `al_mc_edac_irq_handler_ce()` and `_ue()` dispatch interrupt handling. `get_scrub_mode()` maps the controller scrub-disabled bit to EDAC scrub mode. Probe allocates one chip-select layer and configures DIMM metadata.

## Control Flow
Probe maps resource 0, allocates `mem_ctl_info` with private `struct al_mc_edac`, records optional named IRQs `ue` and `ce`, and chooses EDAC interrupt or polling opstate. If either IRQ is absent, the missing side is handled in `al_mc_edac_check()`; if both are present, the driver uses interrupt mode. It initializes EDAC capabilities, scrub mode, and DIMM grain, registers the memory controller, then requests any available IRQs. CE and UE paths read the count first; zero count returns `IRQ_NONE` or no polling event, nonzero count snapshots address/syndrome data, clears hardware count/error bits, formats a message, and reports to EDAC under a spinlock.

## State and Persistence
Driver state is per-controller MMIO base, IRQ numbers, and spinlock stored in `mci->pvt_info`. Hardware holds error counts and first/latest address/syndrome registers until cleared. EDAC core persists event counters in its normal sysfs state. Device-managed cleanup actions free the EDAC allocation and delete the MC registration on teardown.

## Dependencies and Integration Points
The driver depends on device-tree compatible `amazon,al-mc-edac`, platform MMIO resources, optional named IRQs, relaxed MMIO accessors, EDAC MC APIs, and OF IRQ lookup. It reports DDR3/DDR4 SECDED capability and exposes hardware scrub status to EDAC.

## Risks and Edge Cases
The handler clears hardware status before calling EDAC, so a crash during reporting could lose the hardware snapshot. Only one address/syndrome tuple is reported per CE or UE batch count; multiple accumulated errors may be counted but not individually localized. Partial IRQ configurations are intentional but depend on EDAC polling for the missing side. The spinlock serializes EDAC reporting but does not cover the full read/clear sequence.

## Test Signals
Build with `CONFIG_EDAC_AL_MC` and a DT node with MMIO resource and optional `ue`/`ce` IRQs. Runtime signals are successful `edac_mc_add_mc()`, interrupt request success, EDAC CE/UE counters increasing, and messages containing rank/row/bg/bank/column/syndrome fields. Tests should cover both full IRQ mode and missing-IRQ polling fallback.
