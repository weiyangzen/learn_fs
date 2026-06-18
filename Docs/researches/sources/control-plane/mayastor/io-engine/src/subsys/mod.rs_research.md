# sources/control-plane/mayastor/io-engine/src/subsys/mod.rs

## Purpose
This module root registers Mayastor SPDK subsystems and re-exports subsystem-facing APIs.

## Important APIs, Types, And Functions
It re-exports config types, NVMf types, registration types, and `make_subsystem_serial`. `register_subsystem` adds the config subsystem, NVMf subsystem, an SPDK dependency on `bdev`, the registration subsystem, and the NVMx subsystem. `make_subsystem_serial` generates a deterministic `DCS` serial from a SHA-256 hash truncated to SPDK's 20-character serial limit.

## Control Flow
Startup calls `register_subsystem`, which creates SPDK subsystem structures and registers them with SPDK. The NVMf subsystem is registered with an explicit dependency on `bdev`. Other subsystem modules register themselves through their own registration functions.

## State, Persistence, And Dependencies
State is SPDK's subsystem registry and leaked boxed subsystem/dependency structures handed to SPDK. Dependencies include SPDK subsystem functions, config/NVMf/registration/NVMx modules, `sha2`, and `hex`.

## Integration Points
This is the central startup hook for Mayastor subsystem lifecycle. NVMf sharing depends on NVMf registering after bdev. Control-plane registration and NVMe admin queue management are also wired here.

## Risks
Subsystem names and dependency strings are raw nul-terminated byte strings; typos break SPDK ordering. Boxed subsystem/dependency pointers are intentionally leaked to SPDK. Serial generation truncates hashes, which is acceptable but still theoretically collidable.

## Test Signals
Validate subsystem registration order, dependency presence, deterministic serial generation and length, and that exported types remain available to modules using `crate::subsys::*`.
