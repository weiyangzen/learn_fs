# sources/distributed-fs/ceph-client/drivers/clk/stm32/reset-stm32.h

## Purpose

`reset-stm32.h` is the small local interface shared by STM32 RCC clock drivers and `reset-stm32.c`. It defines reset-line descriptors, controller initialization data, and the reset initialization function.

## Important APIs, Types, And Functions

- `struct stm32_reset_cfg` describes one reset bit: RCC register offset, bit index, and whether set/clear-style writes are used.
- `struct clk_stm32_reset_data` passes optional reset ops, explicit reset-line table, line count, and clear offset from SoC drivers to the reset implementation.
- `stm32_rcc_reset_init()` registers a reset controller for the mapped RCC base.

## Control Flow

SoC drivers instantiate `clk_stm32_reset_data` and pass it to `stm32_rcc_reset_init()` from their RCC initialization path. If `reset_lines` is NULL, the implementation derives reset offset/bit from the numeric reset ID and `clear_offset`. If `reset_lines` is present, reset IDs index the explicit table.

## State And Persistence Behavior

The header itself carries no runtime state. It defines the data used to create reset-controller state in `reset-stm32.c`. Hardware reset assertion state persists in RCC registers according to the SoC reset block.

## Dependencies And Integration Points

It assumes Linux reset-controller types are visible to includers. It is included by the STM32 RCC clock drivers and by `reset-stm32.c`. Binding headers supply the numeric reset IDs that index either the generic banked layout or explicit tables.

## Risks And Edge Cases

The `ops` field is currently carried in `clk_stm32_reset_data` but the implementation always installs `stm32_reset_ops`; changing that would require auditing callers. Explicit reset tables must have valid entries for supported IDs and NULL for intentionally inaccessible IDs. `clear_offset` changes behavior globally for generic mappings and per-controller deasserts.

## Test Signals

Compile coverage ensures the structures match users. Runtime validation is through successful reset-controller registration and correct assert/deassert/status behavior for each STM32MP RCC driver.
