# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfswatch/main.go

Purpose: Implements the `ipfswatch` command, a filesystem watcher that imports changed files into an IPFS node and optionally exposes the HTTP API.

Important APIs/types/functions: CLI flags are `--http`, `--repo`, and `--path`. `loadDatastorePlugins` registers datastore plugin parsers. `run` owns watcher setup, repository opening, node construction, CoreAPI creation, optional HTTP serving, event processing, and shutdown. `addTree` recursively watches non-hidden directories. `IsDirectory`, `IsHidden`, and `cmdCtx` are small helpers.

Control flow, state, and persistence: `run` expands the repo path, builds an `fsnotify.Watcher`, recursively adds the initial watch tree, loads datastore plugins, opens the fsrepo, starts an online `core.IpfsNode`, and creates a CoreAPI. The event loop handles SIGINT/SIGTERM, watcher events, and watcher errors. Non-remove events spawn goroutines that open the changed path, wrap it as a Boxo `files.PathFile`, and call `api.Unixfs().Add`. Directory creates add watches recursively; directory removals remove watches. Persistent effects are repository writes from UnixFS imports.

Dependencies and integration points: Integrates `fsnotify`, Kubo config/fsrepo/core/coreapi/corehttp, datastore plugins, Boxo files, and OS signal handling. `cmdCtx` adapts the live node for HTTP command serving.

Risks and test signals: There is minimal synchronization around concurrent add goroutines, no debounce of repeated editor events, and the goroutine closes over event data after the select iteration. Remove events call `IsDirectory` after removal, which can fail and skip watcher removal. Optional HTTP server errors are ignored in the goroutine. Test coverage only checks `IsHidden`.
