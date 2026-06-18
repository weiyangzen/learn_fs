# sources/distributed-fs/ceph-client/drivers/cpufreq/kirkwood-cpufreq.c

## Purpose

`kirkwood-cpufreq.c` is a Marvell Kirkwood cpufreq driver that switches the CPU between two pre-existing clock parents: the normal CPU clock and the DDR clock. It does not synthesize arbitrary rates; it exposes a two-entry cpufreq table populated from device-tree clocks during probe.

## Important APIs, types, and functions

- The file-global `priv` stores the CPU, DDR, and powersave clocks, mapped control register base, and device pointer.
- `kirkwood_freq_table` has two states, `STATE_CPU_FREQ` and `STATE_DDR_FREQ`, whose frequencies are filled from `clk_get_rate()`.
- `kirkwood_cpufreq_target()` blocks CPU software interrupts with `CPU_SW_INT_BLK`, reparents the powersave clock, enters `cpu_do_idle()` so hardware completes the transition, and then restores interrupts.
- `kirkwood_cpufreq_cpu_init()` calls `cpufreq_generic_init()` with a 5000 ns transition latency.
- `kirkwood_cpufreq_probe()` maps the platform resource, fetches CPU node clocks by name, enables them, fills the table, and registers `kirkwood_cpufreq_driver`.

## Control flow

The platform driver probes a `"kirkwood-cpufreq"` device. It obtains CPU0's device-tree node, looks up `cpu_clk`, `ddrclk`, and `powersave`, enables all three clocks, then registers a cpufreq driver. Policy init uses the static table. A target transition selects the table row, disables local IRQs, writes the interrupt block bit in the mapped register, switches the `powersave` parent to CPU or DDR clock, idles the CPU to trigger the hardware transition, clears the block bit, and re-enables IRQs.

## State and persistence behavior

Runtime state is a single global `priv` and a globally mutated two-entry frequency table. Clock parent selection persists in the hardware clock tree until another cpufreq transition. Probe enables all referenced clocks for the driver's lifetime; remove unregisters cpufreq and disables the clocks. There is no suspend/resume-specific state handling.

## Dependencies

The driver depends on a platform device with one MMIO resource, CPU0 device-tree clocks named exactly `cpu_clk`, `ddrclk`, and `powersave`, common clock framework parent switching, ARM `cpu_do_idle()`, and cpufreq generic table helpers.

## Risks and edge cases

- The driver is global and assumes one Kirkwood CPU clock domain; multiple instances would overwrite `priv`.
- `clk_set_parent()` return values are ignored, so a failed reparent is reported as a successful frequency change.
- The transition masks local interrupts and blocks CPU software interrupts; incorrect register mapping or hardware behavior can hang the CPU in idle.
- Frequency table contents are populated at probe only, so later parent clock rate changes are not reflected.

## Test signals

Boot should show successful cpufreq registration and two available frequencies matching CPU and DDR clocks. Runtime tests should switch both states repeatedly, verify `scaling_cur_freq` follows `clk_get_rate(powersave)`, check there are no IRQ stalls, and unload/remove the platform device without leaked prepared clocks.
