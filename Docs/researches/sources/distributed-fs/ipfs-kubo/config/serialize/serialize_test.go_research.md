# Research: sources/distributed-fs/ipfs-kubo/config/serialize/serialize_test.go

Purpose: Tests config file write/read round-trip and file permissions.

Important APIs/types/functions: `TestConfig` writes `.ipfsconfig`, loads it, compares `Identity.PeerID`, stats the file, and checks permissions on non-Windows.

Control flow, state, and persistence: Creates a local `.ipfsconfig` file in the test working directory. It verifies the file is not executable or world-accessible on Unix-like platforms.

Dependencies and integration points: Uses `config.Config`, `WriteConfigFile`, and `Load`. Permission check is skipped on Windows due to Go/os mode differences.

Risks and test signals: The test writes a fixed relative filename and does not clean it up in the snippet, so test isolation depends on working directory conventions. It does not test missing file mapping or atomic failure paths.
