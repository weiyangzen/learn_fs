# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/unix/TestDomainSocketWatcher.java

Purpose: Stress and lifecycle tests for `DomainSocketWatcher`, the background watcher that monitors domain sockets for close/readability notifications and invokes handlers.

Important APIs/types/functions: `DomainSocketWatcher`, `DomainSocketWatcher.Handler`, `DomainSocket.socketpair`, `watcher.add`, `watcher.remove`, `watcher.close`, `watcher.watcherThread`, `CountDownLatch`, `ReentrantLock`, `AtomicInteger`, and `SubjectInheritingThread`.

Control flow: each test is skipped if native domain sockets are unavailable. Simple cases create/close the watcher, add one side of a socketpair, close the peer, and wait for handler notification. Interruption tests interrupt the internal watcher thread. Stress tests concurrently add 250 sockets while another thread randomly closes peer sockets or removes watched sockets until every handler has fired.

State and persistence: state is in the native socket descriptors, watcher thread, watched-socket registry, `trappedException`, and local socketpair list. The `@AfterEach` hook turns any uncaught watcher-thread exception into a test failure.

Dependencies/integration points: native `DomainSocket`, watcher interrupt polling, Guava `Uninterruptibles`, SLF4J logging, and thread inheritance helper.

Risks: inherently concurrent and timing-sensitive; random removal/close order can expose races; native resource cleanup must be reliable; interruption must not leave the watcher thread hanging.

Test signals: verifies notifications are delivered, watched sockets close when watcher closes, thread interruption exits cleanly, and concurrent add/remove/close does not crash the watcher.
