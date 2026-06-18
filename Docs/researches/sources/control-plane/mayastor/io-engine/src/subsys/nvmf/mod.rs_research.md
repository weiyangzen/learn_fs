# sources/control-plane/mayastor/io-engine/src/subsys/nvmf/mod.rs

## Purpose
This module root implements SPDK subsystem registration for the Mayastor NVMf target and exposes NVMf subsystem, target, request, and error APIs.

## Important APIs, Types, And Functions
`Nvmf` wraps an SPDK subsystem pointer. `Error` is the NVMf error enum with errno mapping. `NVMF_PGS` stores thread-local poll groups. The module re-exports admin command helpers, `NvmfSubsystem`, `SubType`, and `Target`. `Nvmf::init`, `fini`, and `new` are SPDK lifecycle callbacks/constructors.

## Control Flow
During SPDK init, `Nvmf::init` registers the custom snapshot admin command. If config enables NVMf, it advances the thread-local target state machine; otherwise it calls `spdk_subsystem_init_next`. During fini, it either starts NVMf target shutdown or advances SPDK fini directly when disabled.

## State, Persistence, And Dependencies
State includes the SPDK subsystem pointer, target state in `target::NVMF_TGT`, and thread-local poll groups. No durable state is stored here. Dependencies include config, JSON-RPC error codes, SPDK subsystem callbacks, poll group and transport modules, and `nix::errno`.

## Integration Points
`subsys/mod.rs` registers this subsystem after config and declares a dependency on bdev. Replica/nexus sharing uses `NvmfSubsystem` and `Target`. Error types map to RPC codes and errno values.

## Risks
NVMf startup is controlled by global config; disabled mode must still let SPDK init/fini proceed. Error-to-errno mapping is coarse for some variants. Thread-local poll groups require correct per-reactor initialization by the target module.

## Test Signals
Test enabled and disabled init/fini paths, custom admin handler registration, error errno mapping, poll group creation through target startup, and SPDK subsystem name/dependency consistency.
