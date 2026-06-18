## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestByteRangeInputStream.java

Purpose: this test validates `ByteRangeInputStream`, the WebHDFS input stream that opens HTTP byte-range requests lazily and reopens after seeks.

Important APIs and types: it defines `ByteRangeInputStreamImpl`, mocks `ByteRangeInputStream.URLOpener` and `HttpURLConnection`, uses `InputStreamAndFileLength`, `StreamStatus`, `Whitebox`, and checks `seek()`, `read()`, `available()`, `close()`, and opener `connect(offset, resolved)` calls.

Control flow: `testByteRange()` reads from the original URL, then from the resolved URL after seeking, verifies seek-to-current-position avoids reconnect, and checks missing `Content-Length` fails. `testPropagatedClose()` drives internal stream status so reopen-on-seek closes only the previous stream and closed streams cannot reopen. Availability tests cover known length, unknown length, read/seek position accounting, and closed-stream errors.

State and persistence: state is in-memory stream position (`startPos`, current position), resolved URL, stream status, wrapped input stream, and optional file length. No network or file persistence occurs because connections are mocked.

Dependencies and integration points: integrates WebHDFS HTTP header handling (`Content-Length`), URL resolution after redirect/open, Hadoop test whitebox utilities, and Mockito partial mocks.

Risks: because transport is mocked, the test validates stream state logic more than real HTTP client behavior. It also reads internal fields and status names, so refactors can require test updates.

Test signals: verifies lazy opening, range offsets after seek, no redundant connection on contiguous reads, propagated close semantics, missing content-length diagnostics, and `available()` behavior for known, unknown, and closed streams.
