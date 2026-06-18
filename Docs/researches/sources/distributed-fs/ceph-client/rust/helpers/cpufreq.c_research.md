# sources/distributed-fs/ceph-client/rust/helpers/cpufreq.c

## Purpose
Exposes cpufreq energy-model registration to Rust when CPU frequency support is enabled.

## APIs, Types, and Functions
`rust_helper_cpufreq_register_em_with_opp()` wraps `cpufreq_register_em_with_opp()` under `CONFIG_CPU_FREQ`.

## Control Flow, State, and Persistence
State is maintained by cpufreq/energy-model subsystems for the provided policy.

## Dependencies and Integration
Depends on `linux/cpufreq.h` and OPP/energy model integration.

## Risks and Test Signals
Risks are config-dependent absence and policy lifetime errors. Test signals are cpufreq-enabled Rust platform driver tests and disabled-config builds.
