# sources/distributed-fs/ceph-client/drivers/reset/reset-eic7700.c

Purpose: ESWIN EIC7700 reset controller with a large static mapping from reset IDs to SYSCRG register offsets and bits.

Important APIs/types/functions: `struct eic7700_reset_data`, `struct eic7700_reg`, `eic7700_reset[]`, `eic7700_reset_assert()`, `eic7700_reset_deassert()`, `eic7700_reset_reset()`, and `eic7700_reset_probe()`.

Control flow: probe maps SYSCRG MMIO as regmap, fills one-cell reset controller metadata, clears the boot flag via `SYSCRG_CLEAR_BOOT_INFO_OFFSET`, waits 50 ms, and registers. Assert clears the mapped bit; deassert sets it; reset does assert, waits 10-15 us, then deassert.

State and persistence: register bits persist in hardware; the boot flag clear changes hardware boot/reset behavior for U84 and SCPU software reset.

Dependencies and integration: built-in platform driver for `eswin,eic7700-reset`, regmap MMIO, dt-binding reset IDs, reset framework.

Risks and test signals: the large table must match dt-bindings and hardware docs exactly. Test representative resets from each register region, boot-flag side effects, invalid ID bounds, and reset polarity.
