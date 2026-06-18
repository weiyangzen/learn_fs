# sources/control-plane/ceph-csi/internal/nvmeof/driver/driver.go

Purpose: Entry point for running the NVMe-oF CSI driver. It initializes shared RBD globals/journals, CSI identity, controller, and node servers, then starts the nonblocking gRPC server.

Important APIs/types/functions: `nvmeofDriver`, `NewDriver`, and `Run`. `Run` configures RBD clone/flatten limits, creates a `csicommon.CSIDriver`, advertises controller and volume access capabilities, chooses node/controller servers based on config flags, starts gRPC, and optionally starts metrics/profiling.

Control flow: If running as controller or combined, controller capabilities include create/delete volume, publish/unpublish, modify, expand, and snapshot create/delete. Access modes include single-node writer, multi-node multi-writer, single-node single-writer, and single-node multi-writer. Server selection is mutually exclusive for node-only and controller-only modes; default starts both.

State and persistence behavior: Persistent data lives in RBD journals and server-specific metadata; this file only sets process-wide RBD globals and creates service instances.

Dependencies and integration points: Integrates with `internal/driver`, `csi-common`, NVMe-oF controller/identity/node packages, RBD driver globals, util config, metrics, profiling, and slow-GRPC middleware configuration.

Risks: RBD global setup is process-wide and shared with any RBD code paths. Capability advertisement must stay aligned with actual method behavior. Node server construction can fail due to kernel module, kernel version, or mount-cache initialization checks, causing process fatal startup.

Test signals: No direct tests for driver startup or capability registration in this subset.
