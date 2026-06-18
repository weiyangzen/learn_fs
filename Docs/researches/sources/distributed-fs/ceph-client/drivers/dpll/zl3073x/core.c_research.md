# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/core.c

## Purpose
This is the common ZL3073x core driver. It identifies chip variants, owns the paged regmap configuration, implements typed register access and HW-register access, initializes and starts DPLL subdevices, maintains the periodic monitor worker, and coordinates devlink registration.

## Important APIs and functions
Exported APIs are `zl3073x_regmap_config`, `zl3073x_dev_probe()`, and register/HW helpers declared in `core.h`: `zl3073x_read_u8/u16/u32/u48()`, `zl3073x_write_u8/u16/u32/u48()`, `zl3073x_poll_zero_u8()`, `zl3073x_mb_op()`, `zl3073x_read_hwreg()`, `zl3073x_write_hwreg()`, `zl3073x_update_hwreg()`, `zl3073x_write_hwreg_seq()`, `zl3073x_ref_phase_offsets_update()`, `zl3073x_dev_start()`, `zl3073x_dev_stop()`, and `zl3073x_dev_phase_avg_factor_set()`. Static chip tables map device IDs to channel counts and feature flags.

## Control flow
Probe reads chip ID/revision/FW/config version, selects `zl3073x_chip_info`, creates a random default clock ID, initializes `multiop_lock`, allocates DPLL channel objects and the worker, starts normal operation, and registers devlink. `zl3073x_dev_start(full)` checks the firmware-ready bit; if not ready it leaves only devlink available for flashing. Full start fetches ref/synth/out/channel state, configures phase measurement, registers each DPLL and its pins, applies initial fine phase adjustment, and queues periodic work. Stop cancels the worker and unregisters DPLLs.

## State and persistence
`struct zl3073x_dev` caches invariant and mutable state for refs, synths, outputs, and channels. The cache is runtime-only; persistent device configuration lives in hardware/flash and is re-read after probe or restart. `phase_avg_factor` and `clock_id` are driver state exposed through devlink/DPLL; `clock_id` defaults randomly but can be changed through devlink driverinit reload.

## Dependencies and integration points
Transport drivers provide `regmap` over I2C or SPI. The core integrates with `dpll.c` for DPLL registration and notifications, `devlink.c` for info/reload/flash, `ref/out/synth/chan` state helpers, and `regs.h` for encoded register addresses. Mailbox register pages 10-14 require `multiop_lock` for coherent multi-register operations.

## Risks and edge cases
Regmap page selection and encoded register size checks are critical. `zl3073x_write_hwreg_seq()` appears to test `seq->wait` rather than `seq[i].wait`, so only the first wait field controls all waits; this is worth review for reset/flash sequences. Firmware not ready intentionally suppresses DPLL registration. Periodic work reads and notifies twice a second, so slow/broken buses can delay notifications.

## Test signals
Probe on known IDs, unknown-ID rejection, firmware-not-ready devlink-only behavior, I2C/SPI regmap access, mailbox lockdep, phase measurement setup, periodic notification behavior, reload restart, and flash-mode enter/leave recovery are the key signals.
