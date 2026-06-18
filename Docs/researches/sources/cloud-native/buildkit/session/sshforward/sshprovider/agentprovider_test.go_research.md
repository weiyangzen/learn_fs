## sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_test.go

Purpose: validates SSH agent provider config handling, especially raw mode.

Important APIs/types/functions: `TestToAgentSource` calls `build.ParseSSH` and `sshprovider.NewSSHAgentProvider` with different CLI-like strings. It creates a temp regular file and a real Unix socket to test path classification.

Control flow: the test first accepts either successful default provider creation or the expected missing SSH_AUTH_SOCK error. It then verifies `raw=true` without exactly one path fails during parsing/provider setup, raw mode with a normal file fails as not a socket, and raw mode with a Unix socket succeeds for both `default=raw=true,<sock>` and `default=<sock>,raw=true` syntaxes.

State and persistence: temp directory, file, and listener are test-scoped. The listener is closed by defer.

Dependencies and integration points: crosses CLI parsing in `cmd/buildctl/build` with provider construction in `sshprovider`.

Risks and test signals: this is Unix-socket oriented; Windows named pipe behavior is covered by platform-specific helper logic but not by this test. It is a strong signal that raw mode constraints are enforced before exposing a provider.
