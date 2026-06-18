# sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/grpc.go

## Purpose
This file implements the real gRPC provider used by BeeSync to communicate with BeeRemote and to initialize local BeeGFS network/auth configuration supplied by Remote.

## Important APIs, Types, and Functions
`grpcProvider` stores the gRPC connection and `beeremote.BeeRemoteClient`. Constants define local files for management TLS cert and auth secret. `init` opens the BeeRemote connection, writes dynamic management/auth materials, and initializes CTL global config. `disconnect`, `updateWork`, and `submitJob` perform provider operations.

## Control Flow
`init` optionally reads a TLS CA file, builds a proxy/TLS-aware client connection, creates the protobuf client, writes management TLS certificate and auth secret when enabled and provided, and calls `config.InitViperFromExternal` with management, auth, remote, worker, and timeout settings. `updateWork` and `submitJob` call the corresponding BeeRemote RPCs and add a TLS-misconfiguration hint for the common server-preface EOF message.

## State and Persistence Behavior
The provider writes BeeGFS management TLS and auth secret files under `/etc/beegfs` with mode `0600`. It initializes global CTL configuration, which cannot currently be changed after first initialization. It owns a gRPC connection that must be closed.

## Dependencies and Integration Points
It depends on `common/beegfs/beegrpc`, `ctl/pkg/config`, protobuf BeeRemote and Flex APIs, gRPC, and runtime CPU count. `beeremote.Client` creates this provider for real Remote addresses.

## Risks and Edge Cases
Updating BeeGFS network config after global Viper initialization is explicitly unsupported and returns an error requiring node restart. Secrets/certs are written to fixed paths, so permissions and filesystem availability matter. `disconnect` assumes `conn` is non-nil. TLS preface EOF hinting is message-string based and advisory only.

## Test Signals
No direct tests cover this file in the subset. Mock-provider tests cover higher-level client behavior, but real TLS/proxy connection setup, file writes, CTL config initialization, and RPC status mapping need integration tests.
