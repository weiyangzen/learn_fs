<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/regulator.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/regulator.c

## Purpose
`regulator.c` provides MMC host helper functions for VMMC, VQMMC, and VQMMC2 regulator discovery and voltage control. It also wires regulator undervoltage events into the MMC core's emergency undervoltage handling path.

## Important APIs, Types, And Functions
Exported helpers include `mmc_regulator_set_ocr()`, `mmc_regulator_set_vqmmc()`, `mmc_regulator_set_vqmmc2()`, `mmc_regulator_get_supply()`, `mmc_regulator_enable_vqmmc()`, and `mmc_regulator_disable_vqmmc()`. Undervoltage helpers are `mmc_undervoltage_workfn()`, `mmc_regulator_register_undervoltage_notifier()`, `mmc_regulator_unregister_undervoltage_notifier()`, and internal `mmc_handle_regulator_event()`. Voltage conversion helpers include `mmc_ocrbitnum_to_vdd()`, `mmc_regulator_get_ocrmask()`, and `mmc_regulator_set_voltage_if_supported()`.

## Control Flow
`mmc_regulator_get_supply()` obtains optional `vmmc`, `vqmmc`, and `vqmmc2` regulators, returns probe defer for unavailable required-at-probe providers, and derives `mmc->ocr_avail` from `vmmc` voltages when possible. `mmc_regulator_set_ocr()` converts a host OCR bit to a voltage range, sets and enables VMMC, or disables it when `vdd_bit` is zero while tracking `mmc->regulator_enabled`. `mmc_regulator_set_vqmmc()` switches signaling voltage for 1.2 V, 1.8 V, or 3.3 V, trying to keep 3.3 V signaling close to VMMC before falling back to the full 2.7-3.6 V range. VQMMC2 currently supports 1.8 V. Undervoltage notifier registration attaches a regulator notifier to VMMC; an under-voltage event sets `host->undervoltage` under lock and queues high-priority work that calls `mmc_handle_undervoltage(host)`.

## State And Persistence
The file updates `mmc->supply` regulator pointers, `mmc->ocr_avail`, `mmc->regulator_enabled`, `mmc->vqmmc_enabled`, `host->undervoltage`, notifier block fields, and delayed/high-priority work state. Hardware-visible persistent state includes regulator enablement and selected voltage levels. Unregister cancels pending undervoltage work after unregistering the notifier.

## Dependencies And Integration Points
It depends on `CONFIG_REGULATOR` for OCR mask derivation and voltage setting, Linux regulator consumer APIs, workqueues, host locking, MMC OCR conversion, and core `mmc_handle_undervoltage()`. Host controller drivers call these helpers from probe and `set_ios()` or voltage-switch callbacks. `mmc.c` provides the bus-level undervoltage handler that can power off and remove a card.

## Risks And Edge Cases
Optional regulators are represented by error pointers and must be checked by callers that require them. `mmc_regulator_set_ocr()` calls the voltage converter without checking its return value, so invalid OCR bits rely on downstream regulator errors. Voltage switching returns a positive value when no change was needed, which callers must not treat as failure. Under-voltage event coalescing depends on `host->undervoltage` and high-priority work; if never cleared by higher layers, later events are ignored. Emergency undervoltage handling can remove the card, so user-visible I/O failures are expected after the event.

## Test Signals
Validation should cover hosts with no regulators, probe deferral, OCR mask derivation from listed and fixed voltages, VMMC enable/disable balancing, VQMMC 1.2/1.8/3.3 V switches including no-change positive returns, VQMMC2 1.8 V, regulator error logging, undervoltage notifier registration/unregistration, event coalescing, cancellation on unregister, and the full path from regulator under-voltage event to MMC card power-off/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/regulator.c -->
