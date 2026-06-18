# sources/cloud-native/containerd/cmd/ctr/commands/images/usage.go

Purpose: implements `ctr images usage`, printing snapshot size/inode usage for an unpacked image chain.

Important APIs/functions: `usageCommand`.

Control flow: validates ref, creates client/context, chooses default snapshotter if unset, gets image metadata, verifies the image is unpacked for that snapshotter, computes chain ID from rootfs diff IDs, then walks parent snapshots by repeatedly calling `Usage()` and `Stat()` until no parent remains, printing a table.

State and persistence: read-only snapshot/image metadata access.

Dependencies/integration: containerd image wrapper, snapshot service, defaults, identity chain ID, progress byte formatter, tabwriter.

Risks: only works after unpack. Parent walking assumes chain IDs map directly to snapshot keys. Error text says "mount" when validating image ref, likely copy/paste.

Test signals: no local tests.
