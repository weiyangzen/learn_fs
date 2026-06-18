# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32-core.h

## Purpose

`clk-stm32-core.h` defines the data contract between STM32MP SoC-specific RCC drivers and the shared STM32 clock core. It describes hardware mux, gate, divider, composite, reset, registration, security, and macro scaffolding used by `clk-stm32mp13.c`, `clk-stm32mp21.c`, and `clk-stm32mp25.c`.

## Important APIs, Types, And Functions

- `struct stm32_mux_cfg`, `stm32_gate_cfg`, and `stm32_div_cfg` describe RCC register offsets, bitfields, flags, optional divider tables, and readiness metadata.
- `struct clock_config` maps a binding ID and security ID to a static clock object plus a registration callback.
- `struct clk_stm32_clock_data` holds SoC tables, gate counters, and optional multi-mux discovery.
- `struct stm32_rcc_match_data` is the per-compatible payload consumed by `stm32_rcc_init()`.
- `struct clk_stm32_mux`, `clk_stm32_gate`, `clk_stm32_div`, and `clk_stm32_composite` are the CCF hardware objects extended with RCC base, lock, SoC data, and table indices.
- `STM32_MUX_CFG`, `STM32_GATE_CFG`, `STM32_DIV_CFG`, and `STM32_COMPOSITE_CFG` generate `clock_config` entries with the correct registration function.

## Control Flow

The header is declarative. SoC files instantiate static `clk_stm32_*` objects with `CLK_HW_INIT*` macros, then add them to `clock_config` arrays using the STM32 macros. At probe time, `clk-stm32-core.c` consumes these descriptors, fills the runtime MMIO/lock/data pointers, and registers each object with CCF.

## State And Persistence Behavior

The header defines in-memory layout only. State becomes live when SoC static objects are registered and their runtime fields are populated. Hardware persistence is handled through the implementation file and RCC registers; the header itself contains no storage except declarations/macros used by SoC source files.

## Dependencies And Integration Points

It includes `<linux/clk-provider.h>` and assumes Linux CCF types, `spinlock_t`, MMIO pointers, device-tree matching, and reset data from `reset-stm32.h`. It is a local ABI: any SoC driver using the shared core must keep IDs, table lengths, security callbacks, and gate counters consistent with these structures.

## Risks And Edge Cases

`NO_ID`, `NO_STM32_MUX`, `NO_STM32_DIV`, and `NO_STM32_GATE` are sentinel values; using them as real indices would access invalid tables. The macro-generated compound-literal casts require the target static object types to match the macro variant. The misspelled security type names in SoC files do not affect this header, but callbacks must still follow the declared `check_security()` signature. Adding fields changes the private STM32 clock-driver contract and requires all participating SoC files to be audited.

## Test Signals

Compiler coverage is the main signal: bad macro/object pairings and missing declarations surface as build failures. Runtime signals are successful probe and correct clock-summary output for every SoC using the shared core. Static analysis should verify table sizes match `GATE_NB`, `MUX_NB`, and `DIV_NB` sentinel counts.
