# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_tcw.h

## Purpose

This header centralizes register offsets and bit definitions for ADDI-DATA timer/counter/watchdog blocks used by several COMEDI drivers. It avoids duplicating TCW register layout constants in each board driver.

## Important APIs, types, and functions

There are no functions or types. The exported preprocessor interface includes offsets such as `ADDI_TCW_VAL_REG`, `ADDI_TCW_SYNC_REG`, `ADDI_TCW_RELOAD_REG`, `ADDI_TCW_TIMEBASE_REG`, `ADDI_TCW_CTRL_REG`, `ADDI_TCW_STATUS_REG`, `ADDI_TCW_IRQ_REG`, and warning-time registers. Bit and field macros cover sync trigger/enable/disable controls, control-mode fields, external clock/gate/trigger selection, timer/counter/watchdog enables, IRQ enable, status flags, and IRQ indication.

## Control Flow

The header has no control flow. Including drivers use these constants to construct `inl()`/`outl()` register accesses for watchdog, timer, and counter operations.

## State and Persistence

No state is stored. The definitions describe hardware register state managed by including drivers.

## Dependencies and Integration Points

The header assumes Linux `BIT()` is available through including source files. It is used by `addi_watchdog.c`, `addi_apci_1564.c`, and other ADDI TCW-capable drivers. The constants form a shared contract between board-specific offsets and common watchdog behavior.

## Risks

Incorrect bit masks here affect every driver using the TCW helper. Some register offsets alias by function, such as value and sync at offset zero, so call sites must know which TCW mode is active. Field macros mask only low bits of inputs, which is convenient but can hide invalid caller values if not separately checked.

## Test Signals

Signals are compile coverage for all including drivers, watchdog arm/ping/reset behavior, timer/counter status bits matching hardware, IRQ-bit recognition, and no divergent local copies of the same TCW constants.
