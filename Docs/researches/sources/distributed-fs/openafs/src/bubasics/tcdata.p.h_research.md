# sources/distributed-fs/openafs/src/bubasics/tcdata.p.h

`tcdata.p.h` is the private template for generated `tcdata.h`, defining tape-coordinator shared data structures and constants for dump/restore task management and volume headers/trailers on tape.

Important types include `struct dumpNode`, which ties a task id to dump/restore arrays, tape set descriptors, parent/level metadata, append mode, and status node; `struct deviceSyncNode`, which wraps a lock and device flags; `struct volumeHeader`, which records volume identity, server/partition, clone/from dates, magic values, continuation, dump set/name/id/level/parent/end/version fields; and small RPC/interface payloads `labelTapeIf`, `scanTapeIf`, `saveDbIf`, and `deleteDumpIf`.

There is no executable control flow. State modeled here is in-memory tape coordinator task state and serialized tape volume metadata. Dependencies include generated `butc.h`, `budb.h`, `bubasics.h`, and `butm.h`.

Risks include fixed magic constants and string sizes, compatibility of on-tape `volumeHeader`, comments noting temporary values, concurrency correctness around `deviceSyncNode.lock`, and alignment/endianness expectations for serialized headers. Test signals are generated header build, dump/restore interop tests that read old tape formats, task abort/done flag behavior, and scan/label/save-db RPC structure compatibility.
