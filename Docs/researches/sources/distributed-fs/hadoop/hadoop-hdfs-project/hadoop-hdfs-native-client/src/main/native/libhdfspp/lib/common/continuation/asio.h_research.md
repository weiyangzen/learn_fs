<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/asio.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/asio.h

## Purpose
Defines a continuation stage that writes an Asio buffer sequence to a stream as part of libhdfspp's continuation-passing async framework.

## Important APIs, Types, And Functions
`asio_continuation::WriteContinuation<Stream, ConstBufferSequence>` stores a shared stream and buffer sequence, and `Write()` allocates the stage. `Run()` calls `boost::asio::async_write` and maps the resulting error code through `ToStatus`.

## Control Flow
When a pipeline reaches the stage, `Run()` starts an async write. The completion handler invokes the pipeline's `next` callback with OK or error status.

## State And Persistence
The continuation owns a shared pointer to the stream and a copy of the buffer sequence until completion. No persistent state exists.

## Dependencies And Integration Points
Depends on `continuation.h`, `common/util.h`, Boost.Asio write, and `Status`. It is used by RPC/DataTransfer protocol code that sends framed data asynchronously.

## Risks
The buffer sequence must reference memory that remains valid through the async write; copying the sequence does not copy pointed-to data for all buffer types. Stages are heap-allocated and owned by `Pipeline`, so callers must not reuse raw pointers.

## Test Signals
Mock-stream tests should verify successful write, error propagation, pipeline sequencing, and lifetime of shared streams and backing buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/asio.h -->
