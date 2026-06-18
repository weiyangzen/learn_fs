# sources/control-plane/ceph-csi/internal/nvmeof/qos.go

Purpose: Defines NVMe-oF gateway QoS parameter names and the value object used by controller and gateway client code.

Important APIs/types/functions: `NVMeoFQosVolume` contains optional pointer fields for read/write IOPS and throughput limits. Constants define CSI mutable parameter keys: `rwIosPerSecond`, `rwMbytesPerSecond`, `rMbytesPerSecond`, and `wMbytesPerSecond`. `String` renders only configured limits or `no QoS limits`.

Control flow: This file has no parsing; controller `parseQoSParameters` builds the struct and gateway `SetQoSLimitsForNamespace` sends pointer fields to protobuf request.

State and persistence behavior: Pure in-memory DTO. Gateway or RBD metadata persistence is handled elsewhere.

Dependencies and integration points: Used by controller mutable-parameter parsing, create/modify volume flows, and gateway namespace QoS calls.

Risks: Pointer fields distinguish unset from explicit zero; callers must preserve that distinction. String labels differ slightly from parameter names but are log-only.

Test signals: Parser tests in `mutable_params_test.go` validate pointer construction and zero handling; no direct test for `String`.
