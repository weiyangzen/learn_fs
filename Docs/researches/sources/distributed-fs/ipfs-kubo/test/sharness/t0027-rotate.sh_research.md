## sources/distributed-fs/ipfs-kubo/test/sharness/t0027-rotate.sh

Purpose: tests identity/key rotation command behavior.

Important control flow: `test_rotate` runs rotation scenarios, captures old/new identities, validates repo config changes, and checks command output. It exercises rotation across supported key types or formats defined in the script and finishes without daemon use.

State and dependencies: mutates `.ipfs/config` identity material and key-related repo state. Depends on Kubo identity generation, config persistence, and peer ID validation helpers.

Risks: identity rotation is destructive if run outside test repos; sharness isolation via `IPFS_PATH` is critical. Test signals are changed PeerID/private key material, successful command exit, and valid rotated identities.
