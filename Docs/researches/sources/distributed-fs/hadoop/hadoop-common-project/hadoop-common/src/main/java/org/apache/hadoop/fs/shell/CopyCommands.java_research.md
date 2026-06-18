# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CopyCommands.java

Purpose: registers and implements copy-family shell commands: `getmerge`, `cp`, `get`, `put`, `copyFromLocal`, `copyToLocal`, and `appendToFile`.

Important APIs and types: outer `registerCommands()`, nested `Merge`, `Cp`, `Get`, `Put`, alias classes `CopyFromLocal`/`CopyToLocal`, and `AppendToFile`. It relies heavily on `CommandWithDestination` and `CopyCommandWithMultiThread` for common destination validation and copying.

Control flow: `Merge` parses newline and empty-file-delimiter options, collects valid source files before opening the local destination, then streams each source sequentially in sorted order. `Cp` parses `-f`, `-d`, `-p[topax]`, thread options, sets recursive copy, and resolves a remote destination. `Get` resolves a local destination, controls checksum verification and local CRC sidecar writes, and can preserve basic metadata. `Put` resolves a remote destination, expands local paths without globbing, supports stdin as a sole `-` source, lazy persist, direct write, overwrite, preservation, and threading. `AppendToFile` creates the remote destination if missing, opens append or new-block append, and streams stdin or local files into it.

State and persistence: commands write local or remote files, append existing remote files, optionally create CRC files, preserve metadata, and create temp `._COPYING_` targets unless direct write is requested. `Merge` keeps `srcs` until all path collection succeeds to avoid partial merged output after a later bad path.

Dependencies and integration: uses `CommandFormat`, `PathData`, `FSDataInputStream`, `FSDataOutputStream`, Java NIO `Files` for local append sources, and `IOUtils.copyBytes()`. It integrates with Hadoop shell command registration via `CommandFactory`.

Risks: `Put` stdin special case passes a synthetic `PathData` for `-` to `getTargetPath()`, so destination naming is sensitive to inherited target logic. `AppendToFile` rejects stdin mixed with file inputs only after destination creation/opening. Threaded copy inherits asynchronous exception aggregation risks. Direct write skips temp-file protection. `Merge` creates/truncates destination only after path collection, but errors during streaming still leave partial local output.

Test signals: cover all option combinations, preserve parsing including `-p` and `-pa`, Windows/local URI parsing, stdin-only `put` and append, `appendToFile -n`, merge delimiter behavior with empty files, source directory recursion depth for merge, and threaded copy error exit codes.
