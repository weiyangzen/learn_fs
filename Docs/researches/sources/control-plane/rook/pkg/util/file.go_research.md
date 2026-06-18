# sources/control-plane/rook/pkg/util/file.go

## Purpose
`file.go` provides small file utilities for logging file contents and creating temporary files with content.

## Important APIs, Types, and Functions
`WriteFileToLog(logger, path)` reads a cleaned path and logs contents or a warning. `CreateTempFile(content)` creates an unnamed temp file in the default temp directory and writes the provided content with mode `0400`.

## Control Flow, State, and Persistence
`WriteFileToLog()` performs read-only filesystem access. `CreateTempFile()` persists a temp file and returns the open file handle; callers are responsible for closing and removing it.

## Dependencies and Integration Points
It depends on `os`, `filepath`, capnslog, and pkg/errors. It integrates with code that needs to expose generated config files in logs or pass temp config files to subprocesses.

## Risks
Logging full file contents can leak secrets if called on sensitive files. `CreateTempFile()` uses `os.WriteFile()` after `os.CreateTemp()`, leaving the original file descriptor open and requiring caller cleanup. Temp files are created in the system default directory.

## Test Signals
No direct mapped tests. Useful signals would cover write/read mode, cleanup responsibility, read failures, and logging redaction expectations.
