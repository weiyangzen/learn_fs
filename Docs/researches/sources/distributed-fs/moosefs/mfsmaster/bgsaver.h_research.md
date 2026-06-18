# sources/distributed-fs/moosefs/mfsmaster/bgsaver.h

This header declares the parent-facing background saver API used by changelog and metadata-transfer code.

The exported calls are `bgsaver_open(speedlimit, ud, donefn)`, `bgsaver_store(data, offset, leng, crc, ud, donefn)`, `bgsaver_close(ud, donefn)`, `bgsaver_cancel()`, `bgsaver_changelog(version, message)`, `bgsaver_rotatelog()`, and `bgsaver_init()`. Completion callbacks receive caller userdata and an integer status.

Callers start a metadata download with `open`, queue one or more offset-addressed chunks with `store`, and finish with `close`. Changelog users queue append and rotation requests; durable success is handled asynchronously by the implementation.

The header exposes no state. The singleton connection and child process own persistence to `metadata_download.tmp` and changelog files. Integration is through `changelog.c`, metadata download workflows, and `init.h`.

Risks are undocumented serialization requirements, callback userdata ownership ambiguity, and limited return information for rotation. Test signals are compile coverage, callback ordering, child failure handling, and background changelog mode integration.
