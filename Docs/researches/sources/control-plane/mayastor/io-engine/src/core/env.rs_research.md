# sources/control-plane/mayastor/io-engine/src/core/env.rs

## Purpose
Owns io-engine process configuration and lifecycle. It parses CLI/environment options, initializes logging, DPDK/EAL, SPDK subsystems, memory pools, reactors, persistent store, gRPC, registration, tracing, and graceful shutdown.

## Important APIs, Types, and Functions
- `MayastorCliArgs` is the clap command surface for gRPC, registration, EAL, memory, pool config, persistent store, events, reactor freeze detection, feature flags, coredump, tracing, and NVMe limits.
- `MayastorEnvironment` is the runtime environment snapshot and global/default store.
- `MayastorEnvironment::new`, `init`, `start`, and `fini` implement process lifecycle.
- `mayastor_env_stop`, `do_shutdown`, `mayastor_signal_handler`, and `signal_trampoline` coordinate graceful shutdown.
- Parsers include `parse_mb`, `parse_ps_timeout`, `parse_crdt`, `parse_grpc_ip`, and feature compatibility parser `delay_compat`.
- Feature access is provided through `MayastorFeatures::get`.

## Control Flow and State
`new` converts CLI args into environment fields and installs the global default. `init` initializes SPDK logging, optionally prints ASAN metadata, loads YAML config, prepares PTPL paths and pool config, initializes EAL, creates I/O context mempools, installs signals, sets feature globals, initializes reactors, launches remote cores, enters the primary SPDK thread, starts tracing, and calls `spdk_subsystem_init` until the RPC server is ready. `start` builds a current-thread Tokio runtime, optionally connects the persistent store, enters master interrupt mode, schedules the user future, and joins gRPC, registration, and reactor futures. Shutdown first stops gRPC/registration, drains nexuses and snapshot rebuilds, exports LVS/LVM pools, finishes RPC and SPDK subsystems, emits stop events, then stops reactors.

Global state includes `GLOBAL_RC`, `SIG_RECEIVED`, `MAYASTOR_FEATURES`, and `MAYASTOR_DEFAULT_ENV`. Persistent effects include PTPL directory creation, persistent-store connection, imported pools, SPDK trace shared memory, and event messages.

## Dependencies and Integration Points
This file is the central integration point for `spdk_rs`, DPDK/EAL, `logger`, `grpc`, `subsys`, `persistent_store`, `nexus`, `lvs`, optional `lvm`, `eventing`, `nic`, `reactor`, and memory-pool initialization. The main binary constructs `MayastorCliArgs` and starts this environment.

## Risks and Test Signals
Startup order is critical: EAL before SPDK subsystems, reactors before cross-core setup, primary thread context before bdev registration, interrupt-mode setup before reactor polling. Several paths panic on unrecoverable init failures. Network selection for NVMf target depends on interface parsing and IPv4/IPv6 preference. Tests should cover CLI defaults, deprecated gRPC endpoint handling, CRDT bounds, persistent-store option propagation, signal idempotence, shutdown ordering, YAML overrides, feature env flags, and target interface detection.
