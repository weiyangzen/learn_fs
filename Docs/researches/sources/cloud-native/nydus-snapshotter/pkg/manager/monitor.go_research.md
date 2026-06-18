# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/monitor.go

This file implements Unix-socket based daemon liveness monitoring with epoll. `LivenessMonitor` defines subscribe, unsubscribe, run, and destroy. `livenessMonitor` tracks subscribers by daemon ID and by file descriptor, using `EpollCreate1` with `EPOLL_CLOEXEC`.

`Subscribe` retries dialing the daemon Unix socket, converts to `*net.UnixConn`, obtains the raw fd, sets it nonblocking, registers `EPOLLHUP|EPOLLERR|EPOLLET`, and records the target. `Run` starts a goroutine that blocks in `EpollWait`, looks up targets, and on HUP/ERR increments daemon-died metrics and sends `deathEvent` to the subscriber channel. `Unsubscribe` removes the fd from epoll, deletes maps, and closes the connection. `Destroy` unsubscribes all and closes the epoll fd, though comments note closing does not wake `EpollWait`.

State is in-memory fd maps and a long-running goroutine. Integration points include manager death handling, daemon API sockets, metrics collectors, retry utilities, and Linux `x/sys/unix`. Risks include Linux-only behavior, event races around unsubscribe, blocked goroutine shutdown, duplicate subscription semantics, and file descriptor lifecycle. Tests exercise death notification and unsubscribe behavior with local Unix servers.
