# sources/distributed-fs/ceph-client/drivers/mfd/si476x-i2c.c

### Purpose
`si476x-i2c.c` is the MFD core and I2C transport driver for Si4761/Si4764/Si4768 tuner devices. It owns power sequencing, regulator and reset control, IRQ or polling status handling, RDS FIFO draining, revision detection, feature predicates, and registration of radio and optional codec children.

### Important APIs, Types, And Functions
Exported APIs include `si476x_core_start()`, `si476x_core_stop()`, `si476x_core_set_power_state()`, `si476x_core_i2c_xfer()`, feature predicates such as `si476x_core_has_am()`, and `si476x_core_is_powered_up()`. Internal functions include `si476x_core_config_pinmux()`, RDS drainer helpers, `si476x_core_pronounce_dead()`, status polling/IRQ handlers, firmware revision mapping, `si476x_core_get_revision_info()`, probe, and remove.

### Control Flow
Probe allocates `struct si476x_core`, initializes a Si476x regmap, requires platform data, requests optional reset GPIO, gets four regulators, initializes locks, wait queues, FIFO, RDS worker, IRQ or polling mode, and chip ID. It powers the device up temporarily to issue FUNC_INFO and map firmware major/function to A10/A20/A30 revision, powers it back down, then creates the `si476x-radio` child and optional `si476x-codec` child when ALSA support and pinmux conditions match. Runtime power-up enables regulators, asserts reset high, enables IRQ or polling, sends POWER_UP, configures pinmux, and enables tuner interrupt sources. Runtime stop clears alive state, optionally sends POWER_DOWN, disables IRQ/polling, and may assert reset low.

### State, Persistence, And Dependencies
Runtime state includes power state, alive/CTS/STC atomics, command and tuning wait queues, command lock, regulator array, reset GPIO, revision, chip ID, platform power/pinmux/diversity parameters, RDS FIFO and worker state, optional delayed polling work, and MFD cells. Persistent hardware effects include power state, pinmux, interrupt enables, tuner mode/frequency/properties via command helpers, and reset state. Dependencies include I2C, regulator bulk APIs, legacy GPIO APIs, regmap helper `devm_regmap_init_si476x()`, kfifo, workqueues, wait queues, MFD core, Si476x command exports, and platform data.

### Integration Points
`si476x-cmd.c` depends on `si476x_core_i2c_xfer()` and the CTS/STC signaling set by this file. The radio child consumes RDS FIFO, tune/status commands, and power-state helpers. Optional codec child creation depends on chip ID and digital-audio pinmux. Systems can run either interrupt-driven mode or polling mode when no IRQ is supplied.

### Risks
The driver requires platform data and has no OF-property parsing in this file. `si476x_core_i2c_xfer()` uses a static `io_errors_count`, so I/O error accounting is shared across all device instances. IRQ/polling startup has delicate ordering around CTS clearing and POWER_UP; polling mode has an explicit workaround for a false first CTS. Remove disables IRQ after `si476x_core_pronounce_dead()`, which wakes waiters, but active child operations still require correct teardown ordering. GPIO uses legacy request/free APIs. If revision detection fails, probe returns `-ENODEV`.

### Test Signals
Tests should cover probe with valid and missing platform data, IRQ and polling modes, regulator failures, reset GPIO paths, revision detection for FM/AM/WB firmware majors, and child creation with/without codec pinmux. Runtime tests should validate power-state transitions, command wait wakeups, RDS drainer FIFO behavior and wakeups, device-dead behavior after repeated I2C errors, and clean remove. Hardware tests should exercise Si4761/Si4764/Si4768 feature predicates, AM availability, diversity mode, and IRQ-source configuration.
