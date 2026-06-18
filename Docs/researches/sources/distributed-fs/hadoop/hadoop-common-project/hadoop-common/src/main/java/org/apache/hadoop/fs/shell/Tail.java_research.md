# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Tail.java

Purpose: implements `-tail`, printing the last 1024 bytes of a file and optionally following appended data.

Important APIs and types: `processOptions()`, `expandArgument()`, `processPath()`, `dumpFromOffset()`, and visible-for-testing `getFollowDelay()`.

Control flow: parses one file, optional `-f`, and optional positive `-s` sleep interval when following. Expansion avoids globbing for backward compatibility. `processPath()` rejects directories, prints from negative offset relative to EOF, then loops while `follow`, sleeping and printing from the last returned offset. `dumpFromOffset()` refreshes file status, normalizes offsets, opens sequential stream, seeks, copies to `System.out`, and returns new position.

State and persistence: no mutation. Follow loop state is current offset and delay.

Dependencies and integration: uses `PathData.openFile()`, `FSDataInputStream.seek()`, and `IOUtils.copyBytes()`.

Risks: output uses `System.out`, not inherited `out`. Follow loop can run indefinitely and exits on interrupted sleep without restoring interrupt status. File truncation while following causes offset > size to return new size without printing. Glob support is intentionally absent.

Test signals: cover no-glob expansion, directory rejection, short/exact/long files, follow delay parsing including zero/negative ignored, appended data, truncation while following, and interrupt exit.
