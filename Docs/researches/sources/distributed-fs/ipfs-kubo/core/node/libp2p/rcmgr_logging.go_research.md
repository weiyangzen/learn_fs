# sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_logging.go

Purpose: wraps a libp2p resource manager to aggregate and periodically log resource-limit-exceeded errors. Important types are `loggingResourceManager` and `loggingScope`.

Control flow: `start` launches a ticker, drains `limitExceededErrs` every interval, logs counts by unwrapped error message, and emits a documentation hint when any occurred. `countErrs` records only `network.ErrResourceLimitExceeded`. The wrapper forwards resource-manager methods and wraps transient/service/protocol/peer scopes so memory reservations and scope assignments are counted. It also implements state APIs such as `ListServices`, `Stat`, and `VerifySourceAddress` when the delegate supports them.

State and persistence: in-memory mutex-protected error-count map; no persistence.

Dependencies/integration: libp2p network/resource-manager interfaces, zap logging, multiaddr. Constructed by `ResourceManager` in `rcmgr.go`.

Risks: many type assertions in `loggingScope` assume the delegate scope implements the requested interface; misuse on the wrong scope type would panic. The wrapper intentionally aggregates logs to avoid noisy per-error output. Tests cover aggregated connection-limit logging.
