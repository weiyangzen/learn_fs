## sources/cloud-native/moby/daemon/attach.go

**Purpose:** Implements daemon-side attach for API clients and raw internal callers, wiring container stdio/log streams to client streams with detach handling, multiplexing, and event logging.

**Important APIs:** `ContainerAttach` validates detach keys, resolves the container, rejects paused/restarting states, builds `stream.AttachConfig`, obtains client streams, optionally muxes stdout/stderr, and delegates to `containerAttach`. `ContainerAttachRaw` is used by builder execution and internal callers. `containerAttach` can replay logs, stream live IO, and handle detach/error outcomes.

**Control flow:** Attach config is registered with `ctr.StreamConfig.AttachStreams`. For log replay, the logger must implement `logger.LogReader`; messages are copied to stdout/stderr according to source. For live streaming, stdin may be buffered through a pipe, disabled if `OpenStdin` is false, and `CopyStreams` runs under the container attach context.

**State and persistence:** No persistent data is written. Runtime state includes stream registrations, goroutines for client disconnect and stdin pipe copying, logger read watchers, and attach/detach events.

**Dependencies and integration:** Uses `stdcopy`, internal `stdcopymux`, `stream.AttachConfig`, container logger APIs, terminal detach parsing, and backend attach config. The classic Dockerfile builder depends on `ContainerAttachRaw` while running build containers.

**Risks:** Goroutine and pipe cleanup depends on context cancellation and stream closure. Log replay uses `context.TODO`, so cancellation is mediated by watcher cleanup rather than request context. StdinOnce waits for container stop, which can block if lifecycle assumptions break.

**Test signals:** No direct tests in this subset. Integration coverage should exercise TTY vs non-TTY muxing, detach key errors, paused/restarting conflicts, logs-only attach, stream disconnect, and raw attach synchronization via the `attached` channel.
