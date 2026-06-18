# sources/distributed-fs/ceph-client/drivers/clk/stm32/reset-stm32.c

## Purpose

`reset-stm32.c` implements the reset-controller side of STM32 RCC drivers. It registers a reset controller backed by RCC MMIO and supports both generic banked reset IDs and SoC-specific explicit reset-line tables.

## Important APIs, Types, And Functions

- `struct stm32_reset_data` stores the reset-controller device, MMIO base, clear-register offset, optional explicit reset-line table, and a spinlock.
- `stm32_get_reset_line()` resolves a reset ID either by banked 32-bit arithmetic or by indexing `data->reset_lines`.
- `stm32_reset_update()` asserts/deasserts reset bits using either set/clear writes or locked read-modify-write.
- `stm32_reset_assert()`, `stm32_reset_deassert()`, and `stm32_reset_status()` implement `reset_control_ops`.
- `stm32_rcc_reset_init()` allocates controller state, fills `reset_controller_dev`, and calls `reset_controller_register()`.

## Control Flow

Each RCC clock driver calls `stm32_rcc_reset_init()` before clock registration. The reset framework then routes consumer reset requests to `stm32_reset_ops`. For generic banked controllers, a reset ID selects `offset = bank * 4` and `bit_idx = id % 32`. For newer SoCs with explicit tables, each binding ID points to a `stm32_reset_cfg` describing register offset, bit, and set/clear behavior.

## State And Persistence Behavior

Software state is the registered reset controller and its static mapping data. Hardware state is the RCC reset bit. Read-modify-write paths are protected by `data->lock`; set/clear paths rely on hardware atomicity. The allocation uses plain `kzalloc_obj()` and `reset_controller_register()`, not devm-managed registration, so lifetime is tied to the traditional non-removable RCC device model.

## Dependencies And Integration Points

The file depends on Linux reset-controller APIs, MMIO accessors, spinlocks, device-tree nodes, and the local `reset-stm32.h` data structures. It is used by STM32MP1, MP13, MP21, and MP25 RCC clock drivers and exposes reset handles to ordinary device-tree consumers.

## Risks And Edge Cases

When `reset_lines` is present, no explicit bounds check is done before indexing by `id`; correctness relies on reset-controller core users passing IDs below `nr_resets`. A NULL table entry returns `-EPERM`, which is intentional for unavailable or secure-owned resets. Generic banked mapping assumes consecutive 32-bit registers starting at the RCC base. Mixed set/clear and read-modify-write semantics must match each reset line or deassert may write the wrong register.

## Test Signals

Build all STM32 RCC drivers. Boot and confirm reset-controller registration under each compatible. Use peripheral drivers or debug instrumentation to assert/deassert timer, serial, SDMMC, USB, Ethernet, display, crypto, and watchdog resets. Verify status reads match hardware and that unavailable table entries fail rather than toggling unrelated bits.
