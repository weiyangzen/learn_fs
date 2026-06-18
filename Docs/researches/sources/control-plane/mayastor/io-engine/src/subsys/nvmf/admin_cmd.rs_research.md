# sources/control-plane/mayastor/io-engine/src/subsys/nvmf/admin_cmd.rs

## Purpose
This file registers and implements a custom NVMe-over-Fabrics admin command for remote snapshot creation.

## Important APIs, Types, And Functions
`NvmeCpl` wraps an NVMe completion and can access status or set `cdw0`. `NvmfReq` wraps an SPDK NVMf request and can complete success or internal-device-error with errno in `cdw0`. `set_snapshot_time` writes current Unix seconds into command dwords 10/11. `decode_snapshot_params` deserializes `NvmeSnapshotMessage` from request data. `nvmf_create_snapshot_hdlr` is the C callback. `create_remote_snapshot` calls `ReplicaOps::create_snapshot`. `setup_create_snapshot_hdlr` registers the opcode handler.

## Control Flow
The handler accepts only subsystems with exactly one namespace. It decodes snapshot parameters, obtains namespace 1 bdev/descriptor/channel, and branches on bdev driver. For published nexuses, it stamps snapshot time and passes the admin command through to the underlying bdev controller. For shared replicas/lvols, it schedules snapshot creation on the master reactor and returns asynchronous request status. Completion is sent after snapshot creation succeeds or fails.

## State, Persistence, And Dependencies
Persistent state is the snapshot metadata/data created by the replica backend. Request state is held in raw SPDK pointers wrapped by `NonNull`. Dependencies include SPDK NVMf request APIs, Mayastor nexus/nvmx snapshot message type, `ReplicaFactory`, reactors, bincode, and errno conversion.

## Integration Points
NVMf subsystem init calls `setup_create_snapshot_hdlr`. Remote hosts can trigger snapshots through the vendor/custom admin opcode. Nexus handling forwards to NVMe passthrough, while replica handling uses local `ReplicaOps`.

## Risks
`decode_snapshot_params` uses `Vec::with_capacity` and copies into the uninitialized buffer pointer, then builds a slice from the raw pointer; this relies on SPDK writing bytes but never sets vector length. The handler returns `-1` for unsupported paths, causing SPDK to handle as unsupported opcode. Raw request wrappers must outlive async snapshot creation. Only single-namespace subsystems are supported.

## Test Signals
Test snapshot message decoding, invalid payload handling, multi-namespace rejection, missing bdev rejection, nexus passthrough with timestamp dwords set, replica async success/failure completion, errno propagation, and custom opcode registration.
