# sources/cloud-native/stargz-snapshotter/analyzer/fanotify/conn/conn.go

Purpose: Defines the small line-oriented stdio protocol used between the analyzer parent process and a fanotify helper process. The protocol messages are `start`, `started`, `ack`, and `fd:<number>`.

Important APIs: `NewClient`, `Client.Start`, `Client.GetPath`, `NewService`, `Service.WaitStart`, `Service.SendStarted`, and `Service.SendFd`. The client sends `start`, waits for `started`, receives file descriptor numbers, resolves them through `/proc/<servicePid>/fd/<fd>`, and acknowledges each descriptor. The service waits for start, signals readiness, sends descriptors, and waits for acknowledgements.

Control flow: `scanWithTimeout` wraps `bufio.Scanner.Scan` in a goroutine and races it with `time.After`. `GetPath` deliberately has no timeout because it is the blocking event stream. `writeMessage` appends a newline so scanner tokenization remains simple.

State and persistence: The only durable state is the external file descriptor held by the service process. In-memory state includes the scanner, service PID, and timeout.

Dependencies and integration: Used by `analyzer/fanotify/fanotify.go` and `analyzer/fanotify/service/service.go`; depends on `/proc` visibility in the client namespace.

Risks: `scanWithTimeout` can leave a blocked goroutine if the timeout wins. Scanner default token size is acceptable for short control messages. Path resolution fails if `/proc/<pid>/fd` is unavailable or the descriptor closes before resolution.

Test signals: No direct tests in this subset; behavior is indirectly exercised by analyzer fanotify flows.
