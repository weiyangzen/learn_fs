# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSck.java`

## Purpose

`DFSck` implements the `hdfs fsck` client. It translates CLI options into NameNode HTTP `/fsck` query parameters, connects to the active NameNode info server, streams fsck output, and returns status codes based on the final NameNode fsck status line. It is a command adapter over server-side `NamenodeFsck`; it does not inspect blocks directly.

## Important APIs, Types, and Functions

- Constructors capture the current `UserGroupInformation`, output stream, timeout-configured `URLConnectionFactory`, and SPNEGO-enabled flag.
- `run` executes `doWork` as the current user.
- `listCorruptFileBlocks` repeatedly calls the `/fsck` endpoint using the `startblockafter` cookie protocol until the server indicates no more corrupt files.
- `getResolvedPath` resolves the user path with the configured filesystem.
- `getCurrentNamenodeAddress` validates the path's filesystem is `DistributedFileSystem` and finds the active NameNode info-server URI via `HAUtil.getAddressOfActive`.
- `doWork` parses fsck options, assembles the URL, opens the connection with optional SPNEGO, streams output, and maps final status text to exit codes.
- `main` handles help and the special ambiguity where `-files` is also consumed by generic option parsing.

## Control Flow

If no path is supplied, `doWork` defaults to `/`. Each recognized flag appends a corresponding query parameter. `-blockId` consumes subsequent non-option tokens into one encoded block ID value. The target path is resolved, stripped of scheme/authority, URL-encoded, and appended as `path=...`. The tool prints the full NameNode URL to stderr, then either enters the corrupt-block listing loop or streams the normal fsck response line by line.

Exit code is derived from the final line: healthy, nonexistent, excess, or bad block ID format map to success; corrupt maps to 1; decommissioned, decommissioning, in-maintenance, entering-maintenance, and stale map to distinct positive codes.

## State and Persistence Behavior

`DFSck` has no durable local state. Server-side operations may mutate HDFS only when the user passes options such as `-move`, `-delete`, or `-replicate`; those changes are performed by NameNode fsck logic. The client stores only connection settings and the authenticated user for the process lifetime.

## Dependencies and Integration Points

It depends on `NamenodeFsck` status constants, HDFS info-server discovery through `DFSUtil` and `HAUtil`, `URLConnectionFactory` for timeout/SPNEGO HTTP, `DistributedFileSystem` detection, `Path` resolution, and `ToolRunner`. Server behavior is an external contract encoded in URL parameter names and text status suffixes.

## Risks and Edge Cases

- The client infers exit status from text output suffixes; changes to server output strings can break exit-code semantics.
- `listCorruptFileBlocks` parses a tab-separated `Cookie:` line as an integer and stops on parse errors.
- If the filesystem is inaccessible or not HDFS, the command prints an error and returns `0` after "DFSck exiting.", preserving legacy behavior but surprising automation.
- `-blockId` parsing consumes multiple non-option tokens and appends spaces before URL encoding.
- The full fsck URL, including path and query flags, is printed to stderr.

## Test Signals

Tests should cover URL generation for every flag, SPNEGO connection errors, status-line-to-exit-code mapping, corrupt-block cookie iteration, access-denied output, non-HDFS filesystem behavior, default path selection, and the `-files` main-method special case.
