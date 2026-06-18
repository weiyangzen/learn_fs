# sources/distributed-fs/ceph-client/include/linux/mfd/stmpe.h

## Purpose

This 163-line header defines the STMicroelectronics STMPE MFD core interface for GPIO, keypad, touchscreen, ADC, PWM, and rotator variants.

## Important APIs, Types, and Functions

It exports ADC/touchscreen configuration macros, STMPE811 ADC registers, `enum stmpe_block`, `enum stmpe_partnum`, register-index enum `STMPE_IDX_*`, `struct stmpe`, bus access helpers `stmpe_reg_read/write`, block read/write, bit update, alt-function, enable/disable, `stmpe811_adc_common_init()`, and the GPIO no-request mask for STMPE811 touch.

## Control Flow

Parent and child drivers use `stmpe_enable()`/`disable()` to manage functional blocks and the bus access helpers to serialize register I/O. Variant-specific register offsets are accessed through `stmpe->regs` indexed by `STMPE_IDX_*`.

## State and Persistence Behavior

`struct stmpe` stores regulators, locks, device/client info, part/variant, register table, IRQ domain, GPIO count, IRQ enable caches, platform data, and ADC config. Hardware persists GPIO, IRQ, ADC, and block-enable state.

## Dependencies and Integration Points

It integrates STMPE MFD parent with I2C/SPI client info, GPIO, keypad, touchscreen, ADC, PWM, IRQ domain, and regulator support.

## Risks and Edge Cases

Register addresses differ by variant, so direct constants are unsafe except where explicitly variant-independent. IRQ enable caches must remain synchronized. Shared ADC settings affect touchscreen and ADC users.

## Test Signals

Variant probe tests, register-index table validation, block enable/disable tests, GPIO IRQ tests, ADC common init tests, and bus access error-path tests.
