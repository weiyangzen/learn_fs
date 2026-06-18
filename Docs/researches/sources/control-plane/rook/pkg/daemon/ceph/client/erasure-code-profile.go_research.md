# sources/control-plane/rook/pkg/daemon/ceph/client/erasure-code-profile.go

Purpose: manages Ceph erasure-code profile discovery, creation, detail lookup, and deletion for erasure-coded pools.

Important APIs/types: `CephErasureCodeProfile` maps Ceph profile JSON with string-encoded `k` and `m`, plugin, technique, failure domain, and CRUSH root. `ListErasureCodeProfiles()`, `GetErasureCodeProfileDetails()`, `CreateErasureCodeProfile()`, and `DeleteErasureCodeProfile()` are the public surface.

Control flow and state: listing and detail lookup are read-only JSON Ceph commands. `CreateErasureCodeProfile()` first reads the `default` profile to inherit plugin and technique, overrides plugin from `pool.ErasureCoded.Algorithm`, builds key/value args for data chunks, coding chunks, plugin, technique, optional failure domain/root/device class, and optional `stripe_unit` bytes, then runs `ceph osd erasure-code-profile set <profile> --force ...` with plain output. `DeleteErasureCodeProfile()` mutates cluster state via `rm`.

Dependencies and integration: depends on `cephv1.PoolSpec`, Kubernetes `resource.Quantity` conversion for `StripeUnit`, and shared command execution. It is integrated with pool creation logic. Risks include relying on the default profile for technique/plugin, stripe unit quantities that cannot be represented as int64 bytes, and destructive `--force` profile updates. Tests cover create argument construction for failure domain, CRUSH root, device class, and stripe unit conversion, but not list/get/delete error paths.
