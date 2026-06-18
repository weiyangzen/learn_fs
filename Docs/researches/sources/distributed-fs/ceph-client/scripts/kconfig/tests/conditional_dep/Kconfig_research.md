# sources/distributed-fs/ceph-client/scripts/kconfig/tests/conditional_dep/Kconfig

## Purpose
This fixture validates conditional dependency syntax `depends on X if Y` for bool and tristate symbols.

## Important APIs, Types, and Functions
It defines `MODULES`, bool `FOO`/`BAR`, bool `TEST_BASIC` and `TEST_COMPLEX`, tristate `BAZ`, and tristate `TEST_OPTIONAL`.

## Control Flow
The parser must turn conditional dependencies into equivalent expressions, and symbol calculation must apply the dependency only when the condition is true.

## State and Persistence
The generated `.config` changes based on supplied test configs.

## Dependencies and Integration Points
Targets parser grammar for `depends`, expression construction, tristate behavior, and oldconfig.

## Risks and Edge Cases
Conditional dependencies can be misinterpreted as unconditional dependencies or lose tristate semantics.

## Test Signals
The paired Python test runs three input configs and compares each output to expected configs.
