# sources/control-plane/mayastor/io-engine/src/subsys/config/opts.rs

## Purpose
This file defines serde-friendly copies of SPDK and Mayastor option structures and conversion code to/from SPDK FFI structs. It centralizes environment overrides for NVMf, NVMe, bdev, socket, and iobuf settings.

## Important APIs, Types, And Functions
`GetOpts` defines `get` and optional `set`. `NexusOpts` controls NVMf enablement/discovery and nexus/replica ports. `NvmfTgtConfig`, `NvmfTgtTransport`, and `NvmfTransportOpts` configure the target and transports. `try_from_env` and `time_try_from_env` parse environment overrides, including humantime durations and backward-compatible unit-suffixed names. `NvmeBdevOpts`, `BdevOpts`, `PosixSocketOpts`, and `IoBufOpts` provide defaults, live getters, setters, and FFI conversions.

## Control Flow
Defaults read `MayastorEnvironment` and environment variables. `Config::apply` calls `set` on option groups that support global SPDK setters. `refresh` calls `get` to convert live SPDK options back into serde structs. NVMf target/transport options are converted into SPDK structs when target/transports are created rather than applied globally.

## State, Persistence, And Dependencies
Option values can be persisted as YAML through `Config`. Live state is in SPDK global option structures. Dependencies include SPDK FFI option APIs, `struct_size_init`, serde, humantime, strum, and `MayastorEnvironment`.

## Integration Points
NVMf target and subsystem code uses `NvmfTgtConfig` and transport options. NVMe bdev connection behavior, socket behavior, bdev I/O pool sizing, and iobuf pool sizing are all controlled here.

## Risks
FFI struct layout changes require updates; compile-time field initialization helps catch many but not all semantic changes. Environment parsing falls back to defaults on invalid values, which can hide misconfiguration unless logs are monitored. Some newer SPDK fields are hard-coded to defaults and not exposed. `PosixSocketOpts::get` asserts SPDK success.

## Test Signals
Test env override parsing, humantime and backward-compatible duration names, invalid env fallback logging, FFI round-trip conversions, setter failure handling, YAML unknown-field rejection, RDMA option overrides, and generated default values from `MayastorEnvironment`.
