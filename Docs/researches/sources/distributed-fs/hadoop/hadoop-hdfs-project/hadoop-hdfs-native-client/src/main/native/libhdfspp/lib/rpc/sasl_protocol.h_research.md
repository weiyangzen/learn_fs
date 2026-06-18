# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/sasl_protocol.h

## Purpose

This header declares `hdfs::SaslProtocol`, the asynchronous client RPC SASL negotiation helper used by libhdfspp connections. It also defines the protocol method string `SASL_METHOD_NAME` as `"sasl message"`.

## Important APIs, types, and functions

The public API is the constructor, destructor, `SetEventHandlers()`, `Authenticate()`, `OnServerResponse()`, and `BuildInitMessage()`. The class derives from `std::enable_shared_from_this<SaslProtocol>` because async RPC callbacks retain the protocol object. Private state is protected by `sasl_state_lock_` and includes the negotiation state enum, cluster name, `AuthInfo`, weak `RpcConnection`, completion callback, `std::unique_ptr<SaslEngine>`, and `LibhdfsEvents`.

## Control flow, state, and persistence

The header documents the threading contract: all entry points must acquire the SASL lock before touching members, and `Authenticate()` must be invoked while the connection lock is already held. Lifecycle is shared-pointer based because Boost.Asio callbacks may outlive the original caller. No data is persisted; the class stores only per-connection authentication state.

## Dependencies and integration points

The header depends on generated RPC protobuf types, `hdfspp/status.h`, `common/auth_info.h`, and libhdfs event plumbing. It forward-declares `RpcConnection`, `SaslEngine`, and `SaslMethod` so users do not need engine implementation headers. `RpcConnection` uses this class to complete authentication and resume normal RPC operation.

## Risks and test signals

Risks are mostly contract risks: missing shared ownership, calling without the right lock, destroying while `state_ == kNegotiate`, or failing to set event handlers. Tests that exercise RPC retry, SASL digest generation, and authentication completion are important regression signals, but direct state-machine unit tests would provide stronger coverage.
