# sources/distributed-fs/ceph-client/include/linux/mfd/stmfx.h

## Purpose

This 122-line header defines register addresses, IRQ/function bits, runtime state, and function enable/disable APIs for the ST STMFX MFD expander.

## Important APIs, Types, and Functions

It exports chip, firmware, system, IRQ, GPIO, direction/type/pull, set/clear register addresses, max register, boot delay, chip/system/IRQ bitfields, `enum stmfx_irqs`, `enum stmfx_functions`, `struct stmfx`, and `stmfx_function_enable()`/`stmfx_function_disable()` prototypes.

## Control Flow

No code flow is local. The parent powers/resets the chip, waits boot time, enables functional blocks through system control bits, and IRQ code uses cached source-enable state under the bus lock.

## State and Persistence Behavior

`struct stmfx` stores regmap, regulator, IRQ domain, lock, IRQ source cache, and suspend/resume backups of SYS_CTRL and IRQ_OUT_PIN. Hardware persists GPIO state, IRQ enables/pending bits, and function enables.

## Dependencies and Integration Points

It includes regmap and integrates STMFX MFD parent with GPIO, touchscreen, IDD, IRQ domain, regulator, and suspend/resume support.

## Risks and Edge Cases

Function enables share SYS_CTRL bits; disabling one block must not disturb another. IRQ source cache must stay synchronized with hardware across suspend/resume. Boot delay is required after reset.

## Test Signals

Function enable reference tests, GPIO IRQ tests, suspend/resume backup-restore tests, boot-delay/probe tests, and regmap max-register checks.
