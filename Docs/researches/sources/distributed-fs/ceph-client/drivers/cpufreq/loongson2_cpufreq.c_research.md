# sources/distributed-fs/ceph-client/drivers/cpufreq/loongson2_cpufreq.c

## Purpose

`loongson2_cpufreq.c` is the Loongson-2F CPUFreq driver. It builds a clock-modulation table from the platform's CPU clock, programs Loongson rate changes through platform helpers, and optionally replaces the architecture `cpu_wait` hook with a Loongson-specific wait sequence.

## Important APIs, types, and functions

- `loongson2_cpufreq_cpu_init()` computes table frequencies from `cpu_clock_freq` and `loongson2_clockmod_table`, sets the initial full rate, and calls `cpufreq_generic_init()`.
- `loongson2_cpufreq_target()` converts a selected table row into a kHz target by multiplying the base clock by the row's divisor data over 8, then calls `loongson2_cpu_set_rate()`.
- `loongson2_cpu_freq_notifier()` updates `current_cpu_data.udelay_val` after cpufreq transitions.
- `loongson2_cpu_wait()` saves `LOONGSON_CHIPCFG`, clears low clock bits to enter wait mode, restores the saved value, and re-enables local IRQs.
- The `nowait` module parameter disables replacement of `cpu_wait`.

## Control flow

Module init registers a platform driver ID table, registers the transition notifier, then registers the cpufreq driver. On success, unless `nowait` is set, it saves the existing `cpu_wait` pointer and installs `loongson2_cpu_wait`. Policy init populates table entries from index 2 upward, because the shared clockmod table encodes fractional eighths, and sets the CPU to full boot rate. Target changes call the board-specific rate setter directly.

## State and persistence behavior

Global state includes `nowait`, `saved_cpu_wait`, the notifier block, and the architecture-global `cpu_wait` pointer. Frequency state persists in Loongson chip configuration registers managed by `loongson2_cpu_set_rate()`. Module exit restores `cpu_wait`, unregisters the cpufreq driver and notifier, and unregisters the platform driver.

## Dependencies

The driver depends on Loongson2EF platform headers for `cpu_clock_freq`, `loongson2_clockmod_table`, `loongson2_cpu_set_rate()`, and `LOONGSON_CHIPCFG`, plus MIPS idle hooks and cpufreq generic helpers. It assumes the platform device name `loongson2_cpufreq`.

## Risks and edge cases

- The file comment says Loongson 2E does not support this feature; platform registration must ensure only supported 2F hardware binds.
- `loongson2_cpu_wait()` calls `local_irq_enable()` after restoring state, so callers must match the expected idle/IRQ context.
- The notifier is registered before cpufreq driver registration and is not unwound if `cpufreq_register_driver()` fails.
- Target changes do not wrap transition notifications locally, relying on cpufreq core behavior around `.target_index`.

## Test signals

Boot should log the Loongson-2F driver, expose the expected fractional table, and keep delay calibration correct after transitions. Runtime tests should switch every table row, verify chip configuration restoration from wait, test `nowait=1`, and unload the module while confirming `cpu_wait` is restored.
