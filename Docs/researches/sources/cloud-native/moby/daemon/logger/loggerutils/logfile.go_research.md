# sources/cloud-native/moby/daemon/logger/loggerutils/logfile.go

Purpose: shared file-backed log persistence, rotation, compression, tailing, and read/follow engine for file-based drivers.

Important APIs/types/functions: `LogFile`, `NewLogFile`, `WriteLogEntry`, `rotate`, `compressFile`, `Close`, `ReadLogs`, `tailFiles`, `openRotatedFiles`, `compressedFileOpener`, `getTailFiles`, `forwarder.Do`, and supporting reader/opener types.

Control flow/state/persistence: `WriteLogEntry` serializes writes, rotates when capacity is reached, writes bytes, updates current position, and notifies waiters. Rotation closes current file, renames/deletes old generations under `fsopMu`, opens a fresh current file, and optionally compresses `.1` asynchronously with last-timestamp metadata in the gzip header. `ReadLogs` atomically captures current file/position, opens rotated files oldest-to-newest, tails with driver-specific tail readers, filters since/until, and follows active writes.

Dependencies/integration: used by json-file and local drivers. Depends on platform file helpers, shared temp decompression, tracing, pools, and driver-supplied `Decoder`/tail reader.

Risks: complex concurrency around `mu`, `rotateMu`, `fsopMu`, and read-state channel. Compression is async, so readers must handle either compressed or uncompressed rotated files. Decode errors while tailing can skip bad files.

Test signals: extensive logfile, race, json/local read, and sharedtemp tests cover rotation, compression, tail, follow, and cancellation.
