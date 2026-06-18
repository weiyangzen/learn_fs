# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/unix/DomainSocketWatcher.java

Purpose: watches a set of `DomainSocket` file descriptors for readability or close events using native polling, then invokes registered handlers.

Important APIs/types/functions: `Handler`, constructor, `close`, `isClosed`, `add`, `remove`, `kick`, `sendCallback`, watcher thread loop, nested `FdSet`, and native `doPoll0`.

Control flow: constructor verifies native support, creates a notification socketpair, and starts a daemon watcher thread. `add` references the socket, queues it, kicks the thread, and waits until processed. `remove` queues by fd and waits until callback/removal. The watcher drains readable fds, processes additions/removals under a lock, checks close/interruption, then polls. `kick` writes one byte to the notification socket and coalesces wakeups to avoid deadlock. Shutdown closes notification socket 0 and joins the thread.

State and persistence: in-memory lock-protected queues `toAdd` and `toRemove`, `closed`, `kicked`, notification sockets, and the thread-local fd set. No persistence.

Dependencies and integration: depends on `DomainSocket`, native libhadoop polling, `IOUtils`, `SubjectInheritingThread`, and Netty-free callback consumers such as HDFS short-circuit cache components.

Risks: handler callbacks run while the watcher lock is held, so slow or reentrant handlers can block add/remove progress. Incorrect fd lifecycle causes native poll on closed descriptors. The final cleanup path must unreference sockets added but never processed.

Test signals: `TestDomainSocketWatcher` covers add/remove, readable callbacks, close cleanup, notification wakeups, and native-availability gates.
