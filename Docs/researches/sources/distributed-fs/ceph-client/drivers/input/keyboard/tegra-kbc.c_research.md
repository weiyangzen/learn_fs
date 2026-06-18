# sources/distributed-fs/ceph-client/drivers/input/keyboard/tegra-kbc.c

## Purpose

This platform driver supports NVIDIA Tegra matrix keyboard controllers. It configures KBC row/column pin routing, debounce/repeat timing, FIFO interrupt processing, optional ghost filtering, and wakeup key handling for Tegra20/30/114 variants.

## Important APIs, Types, and Functions

`struct tegra_kbc` stores device state: timing counts, pin map, keymap, wake flags, MMIO, input, IRQ, spinlock, polling timer, clock/reset, current keys, and variant limits. `tegra_kbc_parse_dt()` reads debounce/repeat, ghost-filter, wake, keymap, and row/column pin arrays. `tegra_kbc_config_pins()` writes row/column pin config registers. `tegra_kbc_report_keys()` decodes FIFO entries, handles optional Fn mapping, filters ghost states, and reports deltas. `tegra_kbc_isr()` transitions from IRQ to timer polling until all keys release.

## Control Flow

Probe selects hardware limits, parses DT, validates pin config, gets IRQ/input/MMIO/clock/reset, computes repoll delay, builds the keymap, requests a disabled high-trigger IRQ, registers input, and marks wakeup. Opening resets/configures hardware, flushes FIFO, clears interrupts, and enables IRQ. FIFO threshold interrupt disables further FIFO interrupts and schedules the timer after the controller's continuous-poll delay. The timer repeatedly reports keys while FIFO count is nonzero, then releases all cached keys and re-enables FIFO interrupts.

## State and Persistence Behavior

`current_keys[]` and `num_pressed_keys` persist currently reported keys. Wake suspend stores continuous-poll timeout in `cp_to_wkup_dly`, switches to keypress wake mode, and records whether wake was caused by a keypress. Hardware configuration is reset and reprogrammed on every input open.

## Dependencies and Integration Points

The driver depends on OF pin arrays (`nvidia,kbc-row-pins`, `nvidia,kbc-col-pins`), matrix-keypad keymaps, platform MMIO/IRQ, reset control, clocks, timers, spinlocks, and input PM locking.

## Risks and Edge Cases

Fn-map fields exist, but this version does not visibly parse a property setting `use_fn_map`, so alternate keymap support may be dormant. Ghost filtering suppresses an entire scan iteration and can delay legitimate chords. Wake resume can synthesize `wakeup_key`, but this field is not populated in the visible code. IRQ disabling and timer deletion must stay ordered to avoid stale timer reads after close/suspend.

## Test Signals

Test Tegra20/30/114 limits, invalid pin arrays, ghost-filter chords, FIFO flush and multi-key events, held-key polling, close during timer activity, wake suspend/resume, reset/clock failures, keymap bounds, and dormant Fn/wakeup-key behavior if platform data expects it.
