# sources/distributed-fs/ipfs-kubo/test/cli/key_test.go

Purpose: verifies exported private key files are written with owner-only permissions.

Important APIs/functions: `TestKeyExportFilePermissions` initializes a node, generates an ed25519 key, and runs subtests for default `libp2p-protobuf-cleartext` and `pem-pkcs8-cleartext` export formats.

Control flow: the test skips Windows, generates `testkey`, exports it to a temporary path in each format, stats the output file, and asserts `0600` permissions.

State and persistence: mutates the node keystore by generating a key and writes exported key material to `t.TempDir` files. No daemon is required.

Dependencies/integration: depends on OS permission semantics, Kubo `key gen/export`, harness CLI execution, and testify assertions.

Risks: permission checks are Unix-specific and can be affected by filesystem mount behavior or umask interactions if command implementation changes. The key is cleartext by design in the tested formats, so temp-file cleanup is important. Test signals are file existence and exact permission bits.
