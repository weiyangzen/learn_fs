# sources/distributed-fs/ceph-client/include/linux/mfd/si476x-core.h

## Purpose

This 531-line header is the central Silicon Labs Si476x radio tuner core interface. It defines core device state, locking helpers, frequency conversions, command argument/report types, command prototypes, status bits, interrupt flags, and property IDs.

## Important APIs, Types, and Functions

Key exports include chip/revision/cell enums, `enum si476x_power_state`, `struct si476x_core`, inline core lock/unlock and frequency conversion helpers, `struct si476x_func_info`, `struct si476x_power_down_args`, tune mode/smoothmetrics/injection-side enums, `struct si476x_rds_status_report`, RSQ/tune args, power/control/query command prototypes, I2C transfer API, interrupt/status bit enums, receiver property enums, RDS/audio property bit enums, and `devm_regmap_init_si476x()`.

## Control Flow

Core runtime flow is serialized by `cmd_lock`: clients power the chip, issue commands, wait on `command`/`tuning` queues for CTS/STC, and process IRQ or polling status. RDS flow uses a kfifo, wait queue, and work item to drain on-chip FIFO. Inline conversions switch frequency units by AM versus FM mode and V4L2 low-frequency units.

## State and Persistence Behavior

`struct si476x_core` holds persistent runtime state: I2C/regmap handles, MFD cells, user count, RDS FIFO, wait queues, atomic CTS/STC/is_alive flags, power-up parameters, power state, regulators, reset GPIO, pinmux, diversity mode, status monitor work, revision, and FIFO depth. Hardware retains tuner state and properties while powered.

## Dependencies and Integration Points

It includes kfifo, atomics, I2C, regmap, mutex, MFD core, V4L2, regulators, and the Si476x platform/report headers. Integration points are MFD child cells for radio/codec, V4L2 tuner operations, command transport, regmap, RDS handling, power management, and diversity support.

## Risks and Edge Cases

Command serialization is critical; bypassing `si476x_core_lock()` can interleave command/status transactions. Frequency conversion depends on current boot function. Polling mode has different RDS FIFO depth. `POWER_INCONSISTENT` prevents unsafe reuse after partial power-down.

## Test Signals

Build tests for radio/codec cells, command mock tests for CTS/STC waits, AM/FM/V4L2 frequency conversion tests, RDS FIFO drain tests, power-state transition tests, and property read/write tests.
