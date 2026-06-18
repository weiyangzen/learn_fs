# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/ipfs-push.go

Purpose: Defines experimental `ctr-remote images ipfs-push`, which optionally converts image layers to eStargz and pushes image content to IPFS.

Important API: `IPFSPushCommand`. Flags select platforms/all-platforms and enable eStargz conversion, defaulting to true.

Control flow: The action validates an image ref, computes the platform matcher, opens a containerd client, chooses an eStargz layer converter if requested, calls `ipfs.Push`, logs the returned CID, and prints it.

State and persistence: Reads image/content from containerd and writes to IPFS through the IPFS package. The command itself maintains no persistent local state.

Dependencies and integration: Uses containerd client/commands, converter types, platform matching, native eStargz converter, and stargz-snapshotter IPFS package.

Risks: Experimental path. Platform selection must match available image manifests. Default eStargz conversion changes layer format unless disabled. IPFS daemon/network errors propagate directly.

Test signals: No direct tests in this subset; likely requires mocked IPFS or integration environment.
