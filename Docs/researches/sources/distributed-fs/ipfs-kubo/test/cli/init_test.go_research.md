# sources/distributed-fs/ipfs-kubo/test/cli/init_test.go

Purpose: validates `ipfs init` output, repo layout, key algorithms, profiles, config defaults, existing-config initialization, and daemon-lock behavior.

Important APIs/functions: `validatePeerID`, `testInitAlgo`, and `TestInit`. It uses peer public-key extraction, libp2p crypto key types, welcome-doc CID from testutils, and harness node commands.

Control flow: `testInitAlgo` runs two variants: empty repo and non-empty welcome-doc repo. It checks exact stdout, repo directories/files, peer ID validity, mount config, and welcome-doc availability. `TestInit` adds failure for unreadable repo dir, ed25519/rsa/default algorithm cases, invalid/valid profiles, server profile config checks, init from an existing config, and refusal while daemon is running.

State and persistence: creates repo directories, config, datastore, blocks, and possibly welcome docs. It reads and validates repo files and starts a daemon only for the lock test.

Dependencies/integration: depends on Kubo CLI init, peer ID extraction behavior, OS permissions, and harness temp repos.

Risks: exact stdout is brittle; permission test may behave differently under privileged users or non-Unix filesystems. Test signals are stdout/stderr strings, file existence, config values, peer key type, and command exit codes.
