<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/terminal.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/terminal.go

### Purpose
`terminal.go` bridges browser/websocket terminal traffic to Kubernetes pod exec streams and provides file/log download helpers for pods. It supports interactive shell sessions, terminal resize messages, heartbeat timeout, direct command output streaming, and safe-ish log export.

### Important APIs, Types, And Functions
`terminalSession` implements `io.Reader`, `io.Writer`, and `remotecommand.TerminalSizeQueue`. `NewTerminalSession` starts heartbeat monitoring. `Write`, `Read`, and `Next` adapt websocket messages to SPDY exec streams. `ExecInPod` opens a TTY exec stream. `DownloadPodFile` streams stdout/stderr from a pod exec command to an `io.Writer`. `DownloadPodLog` streams Kubernetes pod logs into a local file under `/tmp`.

### Control Flow
`Read` receives a websocket message, decodes JSON containing `type`, `data`, `rows`, and `cols`, and returns stdin bytes, queues resize events, responds to pings, or emits the configured end-of-transmission string on protocol errors/default cases. `checkHeartbeat` closes the websocket when no ping has been observed for more than one minute. Exec/download functions build `PodExecOptions`, create a SPDY executor from the REST config and request URL, and call `StreamWithContext`. Log download validates the path prefix, opens the pod log stream, creates/truncates the destination file, copies the stream, and flushes the buffered writer.

### State, Persistence, And Dependencies
`terminalSession` keeps websocket connection state, a size channel, end-of-transmission sentinel, and last heartbeat time. Persistent side effects are local files written by `DownloadPodLog`. Dependencies include `golang.org/x/net/websocket`, Kubernetes client-go REST/SPDY remotecommand, corev1 pod exec/log APIs, and local resource logging.

### Integration Points
Dashboard or troubleshooting components can use this file to exec into mount pods or application pods, download files via `cat`/similar commands, and save pod logs. It sits between HTTP/websocket handlers and Kubernetes API server exec/log subresources.

### Risks
`Next` blocks forever if no resize event arrives; that is normal for the Kubernetes interface but can pin goroutines if streams leak. `Read` returns `0, nil` after resize/ping, which can cause tight read loops depending on caller behavior. The `/tmp` path check is a simple prefix test, so `/tmpfoo` passes and symlinks under `/tmp` are not controlled. `DownloadPodFile` merges stderr into the same writer as stdout. Heartbeat timestamps are updated without synchronization, creating a potential data race under the Go race detector.

### Test Signals
Useful coverage includes websocket stdin/resize/ping/default messages, malformed JSON behavior, heartbeat close after timeout, SPDY executor construction errors, command stream errors, log path rejection outside `/tmp`, copy/flush failures, and cancellation propagation through `StreamWithContext`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/terminal.go -->
