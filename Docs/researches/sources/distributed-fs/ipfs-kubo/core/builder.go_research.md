# Research: sources/distributed-fs/ipfs-kubo/core/builder.go

Purpose: Constructs `IpfsNode` instances using Uber FX, supports global FX option injection, coordinates lifecycle shutdown, and normalizes FX errors.

Important APIs/types/functions: `FXNodeInfo`, `fxOptFunc`, `RegisterFXOptionFunc`, `valueContext`, `BuildCfg` alias, `NewNode`, and `logAndUnwrapFxError`.

Control flow, state, and persistence: `NewNode` saves the caller lifetime context, creates a cancelable context that keeps values but ignores parent cancellation, adds metrics scope, builds FX options from `node.IPFS`, global option funcs, `fx.NopLogger`, and `fx.Extract(n)`, then starts the app. It installs `n.stop` with `sync.Once`, bounded by `cfg.ShutdownTimeout` unless zero, stopping FX before canceling node context. A goroutine stops the node when the lifetime context is canceled. Online nodes run bootstrap after start; offline nodes return immediately. No direct persistence happens here, but dependencies initialize repo-backed subsystems.

Dependencies and integration points: Uses Boxo bootstrap, Kubo core/node, metrics, Uber FX/Dig. Plugin/extension code can globally register option functions affecting all node construction sites.

Risks and test signals: `fxOptionFuncs` is global mutable state without locking; registration order and test isolation matter. Ignoring lifetime cancellation in the working context is subtle but intentional. Shutdown hooks can still run until timeout. Error unwrapping depends on dig private error behavior. No direct tests in this subset.
