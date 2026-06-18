# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketIOWithTimeout.java

Purpose: package-private base for Hadoop socket input/output streams that implement read, write, connect, and readiness waits with explicit timeouts over nonblocking `SelectableChannel`s.

Important APIs/types/functions: constructor, `checkChannelValidity`, abstract `performIO`, `doIO`, static `connect`, `waitForIO`, `setTimeout`, `timeoutExceptionString`, and nested `SelectorPool`.

Control flow: channels are forced to nonblocking mode. `doIO` tries immediate I/O; if zero bytes are transferred, it waits on a pooled selector for the requested operation, throws `SocketTimeoutException` on timeout, and treats close/error as closed. `connect` temporarily sets nonblocking mode, loops on `finishConnect`, closes the channel on failure, and restores blocking mode if needed. `SelectorPool` leases selectors by provider, cancels keys after use, clears cancelled keys with `selectNow`, and trims idle selectors.

State and persistence: per-wrapper state is channel, timeout, and closed flag. Static selector pools are process-local and idle-trimmed after 10 seconds.

Dependencies and integration: used by `SocketInputStream` and `SocketOutputStream`; depends on Java NIO selectors and Hadoop `Time`.

Risks: one thread is intended per wrapper; concurrent use can conflict on channel registration. Negative timeouts are not explicitly rejected. Selector trimming uses static shared state and must avoid returning broken selectors after exceptions.

Test signals: `TestSocketIOWithTimeout` covers timeout behavior, readiness waits, connect timeouts, and selector cleanup.
