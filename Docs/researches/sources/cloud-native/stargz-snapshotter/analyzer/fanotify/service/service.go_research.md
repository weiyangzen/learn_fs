# sources/cloud-native/stargz-snapshotter/analyzer/fanotify/service/service.go

Purpose: Implements the service-side fanotify monitor and an in-process pre-container monitor. It converts kernel fanotify events into fd messages or path sets used for optimization recording.

Important APIs: `Serve(target, r, w)` runs the helper protocol and event loop. `PreContainerMonitor` exposes `NewPreContainerMonitor`, `Start`, `Monitor`, `GetPaths`, and `Close`.

Control flow: `Serve` initializes fanotify with `FAN_CLASS_NOTIF`, waits for the client start message, marks the target mount with `FAN_MARK_MOUNT` for access/open events, sends `started`, then reads `unix.FanotifyEventMetadata` records. Valid event fds are sent to the client via `conn.Service.SendFd`, then closed. `PreContainerMonitor.Start` marks an entire filesystem with `FAN_MARK_FILESYSTEM`; `Monitor` resolves event fds through `/proc/self/fd`, stores paths in a protected set, and exits on EOF, done channel, or fd close.

State and persistence: State is in memory: fanotify file, target dir, path set, done channel, close flags. No persistence.

Dependencies and integration: Uses `golang.org/x/sys/unix` fanotify APIs. `Serve` is invoked by the hidden ctr command; `PreContainerMonitor` is used by analyzer options for GPU/pre-monitor sampling.

Risks: Requires kernel fanotify support and privileges. Queue overflows only print warnings and lose events. `Monitor` can return read errors unless closure is observed. Path capture depends on `/proc/self/fd`.

Test signals: No direct tests; correctness needs privileged integration tests.
