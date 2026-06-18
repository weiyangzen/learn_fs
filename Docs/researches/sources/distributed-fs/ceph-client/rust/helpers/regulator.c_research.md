# sources/distributed-fs/ceph-client/rust/helpers/regulator.c

## Purpose
Provides Rust helper wrappers for regulator APIs when the regulator framework is not built as real callable functions.

## APIs, Types, and Functions
Under `!CONFIG_REGULATOR`, exports put/get, set/get voltage, enable/disable/is_enabled, and device-managed get-enable helpers including optional form.

## Control Flow, State, and Persistence
State is regulator references, enable counts, and voltage constraints maintained by regulator core or stubs.

## Dependencies and Integration
Depends on `linux/regulator/consumer.h` and Rust power-management driver abstractions.

## Risks and Test Signals
Risks include config-dependent stub semantics, unbalanced enable/disable, leaked references, and optional regulator error handling. Test signals are driver tests with regulator enabled/disabled and probe-failure cleanup.
