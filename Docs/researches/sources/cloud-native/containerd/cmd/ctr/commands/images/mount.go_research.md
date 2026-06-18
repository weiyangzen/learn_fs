# sources/cloud-native/containerd/cmd/ctr/commands/images/mount.go

Purpose: implements `ctr images mount`, unpacking an image and mounting or activating a snapshot view/prepare for inspection.

Important APIs/functions: `mountCommand`.

Control flow: validates image ref, derives snapshot/lease key from target or random suffix, creates client/context, chooses default snapshotter if unset, creates a lease with expiration, parses platform, loads image metadata, unpacks image for the platform, computes chain ID from rootfs diff IDs, creates a read-only view or writable prepare snapshot, optionally reuses existing mounts, activates through mount manager when supported, mounts to target or uses a bind source when target omitted, prints chain ID and target.

State and persistence: creates lease, snapshot view/prepare, may mount filesystem at target, and may activate mount manager state. On returned error, deferred cleanup releases lease if created.

Dependencies/integration: image service, snapshot service, mount manager, diff sync-fs, leases, defaults, platforms, identity chain ID.

Risks: target omitted only works when a single bind mount is returned. If mount fails, snapshot cleanup is attempted but can fail and only prints to err writer. Random key uses three random bytes plus nanosecond, sufficient for CLI but not globally collision-proof.

Test signals: no local tests; mount behavior is integration/system dependent.
