# sources/control-plane/ceph-csi/internal/nvmeof/util.go

Purpose: Provides small NVMe-oF utility helpers for UUID normalization and hostname-to-IP resolution.

Important APIs/types/functions: `formatUUID` removes dashes and parses a UUID into standard dashed format, returning the original input if parsing fails. `ResolveIPAddress` calls `net.LookupHost` and returns the first address.

Control flow: `formatUUID` is used by namespace device lookup to try `/dev/disk/by-id/nvme-uuid.*` symlink variants. `ResolveIPAddress` is used when listener address is `0.0.0.0` and nodes must resolve the gateway hostname.

State and persistence behavior: No persistent state. DNS resolution depends on node runtime resolver state.

Dependencies and integration points: Depends on `google/uuid` and Go `net`. Integrated with `nvmeof_initiator.ResolveListeners`.

Risks: `ResolveIPAddress` returns the first record only and has a TODO for IPv6 behavior. Invalid UUIDs are silently passed through, which is intentional but can delay failure to device lookup.

Test signals: `util_test.go` covers UUID formatting for dashed, malformed, and empty strings. DNS resolution is not unit tested.
