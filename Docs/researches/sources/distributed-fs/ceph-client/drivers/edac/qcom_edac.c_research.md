# sources/distributed-fs/ceph-client/drivers/edac/qcom_edac.c

## Purpose
Implements EDAC device reporting for Qualcomm LLCC ECC errors. It configures LLCC ECC interrupt propagation, dumps DRAM and tag RAM syndrome/count/way registers per bank, clears error status, and reports LLCC data/tag RAM CE and UE events.

## Important APIs, Types, And Functions
- `edac_reg_data[]` describes the syndrome register count, count masks, way masks, and shifts for DRAM/TRAM CE/UE classes.
- `qcom_llcc_core_setup` enables TRP/DRP interrupt paths and sets the single-bit threshold.
- `qcom_llcc_clear_error_status` clears DRP or TRP interrupt and counter registers.
- `dump_syn_reg_values` reads syndrome, count, and way registers for a bank and error type.
- `dump_syn_reg` maps dumped error types to EDAC CE/UE handlers.
- `llcc_ecc_irq_handler` scans all LLCC banks for DRP/TRP single- or double-bit status.
- `qcom_llcc_edac_probe` allocates the EDAC device and selects interrupt or polling mode.

## Control Flow
Probe receives `llcc_drv_data` through platform data. If firmware/LLCC has not configured ECC IRQ routing, it programs the broadcast regmap. It allocates one EDAC device with one logical `qcom-llcc` instance and one block per bank, sets `panic_on_ue`, tries to request the provided IRQ, and falls back to five-second polling when no IRQ is usable. The IRQ/poll handler iterates banks, reads DRP status then TRP status, dumps and clears the first matching CE or UE class for each, and marks the interrupt handled when register operations succeed.

## State And Persistence
Driver-private state is the EDAC device; LLCC topology and register maps live in `llcc_drv_data` supplied by the LLCC core. Hardware interrupt enables, thresholds, syndrome registers, counters, and clear registers persist in LLCC hardware. Remove deletes and frees the EDAC device but does not undo LLCC interrupt configuration.

## Dependencies And Integration Points
Depends on `linux/soc/qcom/llcc-qcom.h`, LLCC-provided regmaps and register offsets, EDAC device APIs, and platform device ID `qcom_llcc_edac`. It integrates with either IRQ delivery or EDAC polling.

## Risks And Edge Cases
The handler uses `else if`, so if a bank reports both CE and UE for DRP or TRP, only the CE path is handled first. It sets `irq_rc = IRQ_HANDLED` whenever the status read succeeds, even if no error bit was set, after each DRP/TRP read. `panic_on_ue` is enabled, so uncorrectable LLCC errors can intentionally panic depending on EDAC policy. Clear-on-dump means syndrome data is lost after reporting.

## Test Signals
Validate core setup writes, IRQ and polling fallback paths, each DRAM/TRAM CE/UE status bit, multi-bank iteration, simultaneous CE/UE behavior, syndrome/count/way prints, clear-register writes, and remove without LLCC state leaks.
