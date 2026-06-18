## sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider.go

Purpose: builds a session attachable that exposes one or more SSH agents or private-key files to the BuildKit daemon, with optional raw socket passthrough.

Important APIs/types/functions: `AgentConfig` carries ID, paths, and `Raw`. `AgentConfig.toDialer` normalizes paths, applies SSH_AUTH_SOCK/default fallback, and enforces raw mode constraints. `NewSSHAgentProvider` validates unique IDs and returns a `socketProvider`. `toDialer` converts one socket, one Windows pipe, or multiple private key files into a `dialerFn`. `source.agentDialer` serves an `agent.Agent` over `net.Pipe`; `readOnlyAgent` blocks mutating operations against a forwarded real agent.

Control flow: configs are normalized to IDs, then each path is classified as Windows pipe, Unix socket, or private key file. Sockets are either returned raw or wrapped in a read-only SSH agent server. Key files are limited to 100 KiB reads, parsed with `ssh.ParseRawPrivateKey`, and added to an in-memory keyring. Mixing sockets and keys is rejected.

State and persistence: maintains only in-memory keyrings and socket dialer paths. It reads key files but does not persist them. Real agents are protected by a read-only wrapper for add/remove/lock/extension operations.

Dependencies and integration points: integrates with `sshforward` service, Go crypto SSH agent package, OS socket probing, and Windows pipe helpers. Build CLI parsing feeds these configs.

Risks and test signals: passphrase-protected private keys are not supported. `Uploader.Add`-style locking is not used here, but config creation is single-threaded. Raw mode deliberately exposes the socket protocol. Tests cover missing default agents, raw-mode path count, non-socket raw rejection, and Unix socket acceptance.
