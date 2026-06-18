# sources/distributed-fs/ceph-client/drivers/mfd/si476x-cmd.c

### Purpose
`si476x-cmd.c` implements the command protocol for Silicon Labs Si476x AM/FM tuner chips. It serializes command bytes over the core I2C transfer primitive, waits for command-complete and tune-complete signals maintained by the I2C core, parses responses into typed reports, and exports command helpers used by radio/audio child drivers and the MFD core.

### Important APIs, Types, And Functions
The key internal engine is `si476x_core_send_command()`, with helpers `si476x_core_parse_and_nag_about_error()`, `si476x_cmd_tune_seek_freq()`, and `si476x_cmd_clear_stc()`. Exported APIs include property get/set, pinmux commands, power up/down, AM/FM tune and seek, AM/FM RSQ status, ACF status, FM RDS status/blockcount, phase diversity, AGC status, and FUNC_INFO. A revision vtable selects A10, A20, or A30 implementations for commands with firmware-specific argument/response layouts.

### Control Flow
Each command helper builds an argument byte array, calls `si476x_core_send_command()`, and optionally parses response bytes. The send path validates argument count, sends command plus arguments through `si476x_core_i2c_xfer()`, clears CTS after the write, waits on `core->command` for CTS, performs an extra POWER_UP wait in polling mode, reads the response, checks the device error bit, optionally fetches an extended error code, and returns success only if CTS is set. Tune/seek helpers clear STC, send the command with tune timeout, wait on `core->tuning`, then acknowledge STC through RSQ status.

### State, Persistence, And Dependencies
This file owns no long-lived state but mutates `core->cts` and `core->stc` through command flow and writes persistent tuner properties, pinmux, power, tune, seek, and diversity settings. Dependencies include wait queues and atomics from the core, I2C transfer exported by `si476x-i2c.c`, unaligned big-endian helpers, V4L2 RDS block constants, Si476x public structures/enums, and firmware revision stored in `core->revision`.

### Integration Points
`si476x-i2c.c` uses power and FUNC_INFO commands during startup and revision detection, and uses RDS/status commands in interrupt and worker paths. Radio child drivers use exported tune, seek, status, RDS, AGC, ACF, property, and diversity helpers. Codec support depends on pinmux configuration commands issued by the core startup path.

### Risks
The exported revision-dispatch functions use `BUG_ON()` if `core->revision` is unset or above A30, so bad revision detection can crash the kernel rather than returning an error. `si476x_core_cmd_func_info()` fills the output structure even if the command failed, using response buffer contents. `argn > CMD_MAX_ARGS_COUNT` returns `-ENOMEM` even though the condition is an argument-size error. Wait timeouts only warn; the code still reads a response and may then fail later. Large response parsers are hand-coded and susceptible to byte-offset mistakes.

### Test Signals
Tests should mock I2C transfers for each command revision path, including error-bit responses and extended error codes. Hardware tests should cover power up/down on A10/A20/A30 firmware, FM/AM tune and seek STC handling, property read/write, pinmux commands, RDS FIFO reads, AGC/RSQ/ACF parsing, and phase diversity status. Negative tests should cover timeout, short I2C send/receive, busy/error codes, null report arguments, and unsupported revisions before vtable dispatch.
