# sources/control-plane/ceph-csi/internal/nvmeof/nvmeof.go

Purpose: Implements the management-plane gRPC client wrapper for the Ceph NVMe-oF gateway. It exposes higher-level operations for subsystems, namespaces, listeners, hosts, QoS, and gateway metadata conversion.

Important APIs/types/functions: `GatewayAddress`, `ListenerDetails`, `GatewayConfig`, `GatewayRpcClient`, `NewGatewayRpcClient`, `Destroy`, namespace operations, subsystem operations, host/listener operations, `UpdateHostsForSubsystem`, `ListNamespaces`, `ListListeners`, `ConvertListenersFromProto`, `generateSerialNumber`, and `findExistingNamespace`.

Control flow: Construction applies default management port 5500 and creates a gRPC client using insecure transport. Namespace creation calls `NamespaceAdd`, treats EEXIST by listing existing namespaces and matching pool/image, and returns namespace ID. Subsystem creation generates a random Ceph-prefixed serial, enables HA, optionally passes network masks, and treats EEXIST as success. Listener/host delete and add paths normalize several gateway status codes into idempotent success. QoS maps gateway EEXIST into `ErrRbdQoSExists`. Host update reconciles current versus desired hosts by remove-then-add.

State and persistence behavior: The client holds a gRPC connection and config only. Durable state is on the NVMe-oF gateway and backing RBD images. Serial numbers are generated randomly under gateway constraints.

Dependencies and integration points: Depends on `github.com/ceph/ceph-nvmeof/lib/go/nvmeof` protobufs, gRPC, gateway status codes expressed as errno values, `nvmeof/errors`, and controller orchestration.

Risks: Insecure gRPC transport is hard-coded. IPv4 address family is assumed for listeners. Gateway API status-code semantics are embedded in client behavior and must track gateway changes. Host reconciliation uses `slices.Contains`, so large host lists are O(n*m). `Destroy` clears config and client, making the object unusable after close.

Test signals: Unit tests cover address string formatting, deterministic serial edge case, NVMe list-subsys JSON parsing in the initiator package, and an environment-gated real gateway test covers a subset of subsystem/host/listener operations. Many gateway error/status branches are untested.
