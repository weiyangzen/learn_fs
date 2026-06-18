# sources/distributed-fs/ipfs-kubo/test/cli/identity_cid_test.go

Purpose: regression suite for identity-hash CID size limits and MFS conversion behavior when inline data would exceed `verifcid.DefaultMaxIdentityDigestSize`.

Important APIs/functions: `TestIdentityCIDOverflowProtection` covers `ipfs add --hash=identity`, `ipfs add --inline --inline-limit`, `ipfs files write --hash=identity`, `ipfs block put --format=raw --mhtype=identity`, `cid format`, and `files stat/read`.

Control flow: each parallel subtest creates a node, writes temp files, invokes add/files/block commands, and asserts either identity hash use or fallback to `config.DefaultHashFunction`. MFS append cases start from identity CIDs and verify overflow converts to a cryptographic hash or UnixFS dag-pb structure.

State and persistence: creates files in node repos, writes to MFS paths, adds blocks, and mutates the local blockstore/MFS root. No network state is required beyond the daemon.

Dependencies/integration: depends on Boxo `verifcid`, Kubo default hash config, harness process helpers, and file system operations.

Risks: extracting CID with `strings.Fields(stdout)[1]` assumes `ipfs add` output format. Parallel daemon-heavy subtests can be slow. Test signals include command failure text, CID multihash names/codecs, MFS hashes, and read-back content.
