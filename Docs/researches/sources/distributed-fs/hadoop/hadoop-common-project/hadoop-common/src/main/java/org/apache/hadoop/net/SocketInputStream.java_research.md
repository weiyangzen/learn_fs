# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketInputStream.java

Purpose: `InputStream` and `ReadableByteChannel` wrapper that reads from a selectable socket channel with Hadoop-managed timeouts.

Important APIs/types/functions: constructors from `ReadableByteChannel` or `Socket`, `read()`, `read(byte[], int, int)`, `read(ByteBuffer)`, `close`, `getChannel`, `isOpen`, `waitForReadable`, and `setTimeout`.

Control flow: a nested `Reader` implements `SocketIOWithTimeout.performIO` by calling `ReadableByteChannel.read`. All channel reads pass through `reader.doIO(..., OP_READ)`. Closing closes the underlying channel and marks the reader closed.

State and persistence: holds only the `Reader`; no persistence. Constructing the wrapper makes the socket channel nonblocking, which changes behavior of standard socket streams.

Dependencies and integration: used by `NetUtils.getInputStream` and by `SocketInputWrapper` for sockets with channels. Pairs with `SocketOutputStream`.

Risks: sockets created without a channel fail construction. Single-byte reads allocate a new byte array. Consumers must avoid mixing this wrapper with the original blocking socket streams after nonblocking mode is set.

Test signals: `TestSocketIOWithTimeout` exercises reads, EOF, timeout, close, and channel validity behavior.
