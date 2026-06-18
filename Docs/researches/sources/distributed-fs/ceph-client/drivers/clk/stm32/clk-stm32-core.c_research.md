# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32-core.c

## Purpose

`clk-stm32-core.c` is the shared STM32 RCC common-clock helper used by newer STM32MP clock drivers. It turns SoC-specific `clock_config` tables into registered CCF providers, exposes generic STM32 mux/gate/divider/composite operations, and wires reset initialization through the local reset helper.

## Important APIs, Types, And Functions

- `stm32_rcc_init()` is the public entry point. It matches the device node, initializes RCC resets, then registers all clocks.
- `stm32_rcc_clock_init()` allocates `clk_hw_onecell_data`, pre-fills unresolved IDs with `ERR_PTR(-ENOENT)`, skips secure clocks through `check_security`, invokes each `clock_config->func`, and registers an OF clock provider.
- `stm32_mux_get_parent()` and `stm32_mux_set_parent()` read/write SoC mux descriptors from `clk_stm32_clock_data`.
- `stm32_gate_endisable()`, `stm32_gate_disable_unused()`, and `stm32_gate_is_enabled()` implement gate reference counting and set/clear-register support.
- `stm32_divider_get_rate()` and `stm32_divider_set_rate()` share Linux divider table/flag semantics, including one-based, power-of-two, table, read-only, and hiword-mask modes.
- `clk_stm32_mux_ops`, `clk_stm32_gate_ops`, `clk_stm32_divider_ops`, and `clk_stm32_composite_ops` are the exported CCF operation sets.
- `clk_stm32_*_register()` functions bind static SoC clock objects to the mapped RCC base, shared spinlock, and SoC clock-data tables before `devm_clk_hw_register()`.

## Control Flow

Platform drivers map the RCC register block and call `stm32_rcc_init()`. The function first calls `stm32_rcc_reset_init()`, then iterates the SoC `tab_clocks` list. Each clock entry selects one of the local register helpers through macros in the header. At runtime, CCF calls the corresponding ops to set mux parents, gate clocks, change divider-backed rates, or handle composites with gate, mux, and divider pieces.

Composite parent changes update the hardware mux under the shared spinlock. If the SoC provides `is_multi_mux`, sibling clocks sharing a hardware mux are reparented in CCF after a parent switch. Safe muxes are parked at parent index 0 when disabled and restored to the CCF-selected parent when enabled, avoiding unsafe inactive-source selections.

## State And Persistence Behavior

The driver keeps minimal software state: per-gate counters from `clock_data->gate_cpt`, object back-pointers to MMIO base/lock/SoC data, and CCF registration state. Hardware register state persists in the RCC block until reset or another agent modifies it. Gate counters prevent disabling a shared hardware bit while multiple logical clocks still use it; they are not persisted across reboot.

## Dependencies And Integration Points

It depends on Linux CCF, OF clock providers, MMIO accessors, spinlocks, and the sibling `reset-stm32` helper. SoC drivers provide arrays of `stm32_gate_cfg`, `stm32_mux_cfg`, `stm32_div_cfg`, `clock_config`, reset data, security callbacks, and optional multi-mux callbacks. Consumers only see normal CCF clock IDs from each SoC binding.

## Risks And Edge Cases

Incorrect gate counter sizing or gate IDs can corrupt adjacent counters and cause stuck-on or prematurely disabled clocks. Shared set/clear offsets must match the hardware register layout. `clk_stm32_divider_set_rate()` returns `rate` when `NO_STM32_DIV` is used, which is positive and could be surprising if called in a path expecting `0` for success; current composite/divider definitions avoid relying on that for real divider-less clocks. Safe-mux handling assumes parent index 0 is safe. Multi-mux reparenting must stay aligned with the SoC tables or CCF may disagree with hardware.

## Test Signals

Build all STM32MP RCC drivers that use this core. Boot a supported board and confirm `/sys/kernel/debug/clk/clk_summary` lists expected gates, muxes, dividers, and composites. Exercise parent switching for shared mux groups, enable/disable paired logical clocks sharing one gate, and run suspend/resume or late `clk_disable_unused` to catch unsafe parking or reference-count errors.
