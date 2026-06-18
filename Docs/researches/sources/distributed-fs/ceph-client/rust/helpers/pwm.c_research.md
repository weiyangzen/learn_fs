# sources/distributed-fs/ceph-client/rust/helpers/pwm.c

## Purpose
Exposes PWM chip parent and driver-data helpers to Rust PWM drivers.

## APIs, Types, and Functions
APIs are `pwmchip_parent`, `pwmchip_get_drvdata`, and `pwmchip_set_drvdata` wrappers.

## Control Flow, State, and Persistence
State is PWM chip drvdata and parent device reference owned by the PWM core/driver.

## Dependencies and Integration
Depends on `linux/pwm.h` and Rust PWM abstractions.

## Risks and Test Signals
Risks include drvdata type confusion and chip lifetime misuse. Test signals are Rust PWM chip registration tests.
