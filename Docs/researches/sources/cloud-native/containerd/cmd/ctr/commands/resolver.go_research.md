<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/resolver.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/resolver.go

## Purpose
Builds registry resolvers and static credential helpers from ctr global registry flags.

## Important APIs, Types, And Functions
Exports `PushTracker`, `GetResolver`, `NewStaticCredentials`, and `staticCredentials.GetCredentials`; internal helpers handle password prompting and TLS config.

## Control Flow
Credentials are parsed from `--user` or `--refresh`, prompting with echo disabled when needed. Host options wire credentials, plain HTTP, TLS roots/client certs, hosts-dir overrides, and optional request dumping before constructing a Docker resolver.

## State And Persistence
Maintains process-local push tracking in memory; reads certificate files and terminal input but does not write persistent data.

## Dependencies And Integration Points
Uses containerd remotes/docker config, registry credential helper interfaces, console echo controls, x509/tls, and HTTP debug dumping.

## Risks And Test Signals
`--skip-verify` weakens TLS; prompting assumes an interactive console. Static credentials return only for the exact ref. No direct tests visible here. Source size reviewed: 199 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/resolver.go -->
