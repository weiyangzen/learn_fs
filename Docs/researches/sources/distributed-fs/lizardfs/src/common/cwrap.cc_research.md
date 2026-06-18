# sources/distributed-fs/lizardfs/src/common/cwrap.cc

Purpose: implements small RAII and exception wrappers over POSIX/C filesystem APIs.

Important APIs/types/functions: `FileDescriptor` constructors/destructor, `get`, `reset`, `close`, `isOpened`; deleters `CFileCloser` and `CDirCloser`; `errorString`; namespace `fs` functions `exists`, `rename`, `remove`, `dirname`, `getCurrentWorkingDirectory`, and `getCurrentWorkingDirectoryNoThrow`.

Control flow: `FileDescriptor` closes an owned fd on reset/destruction. Filesystem wrappers call C APIs and throw `FilesystemException` on errors except `exists`, which treats `ENOENT` as false. `getCurrentWorkingDirectoryNoThrow` catches `FilesystemException`, logs a warning, and returns `"???"`.

State and persistence: `FileDescriptor` owns one fd in memory; wrappers mutate the filesystem through rename/remove but keep no persistent state themselves.

Dependencies and integration: depends on `cwrap.h`, `exceptions.h`, `massert`, `libgen`, `unistd`, and syslog helpers through exception/logging headers. It centralizes errno-to-exception behavior.

Risks: `FileDescriptor::close` ignores `::close` failure and asserts only that the fd was open. `dirname` uses `strdup` without checking null. `errorString` wraps `strerror`, which may be thread-local or static depending on platform.

Test signals: no direct tests in subset; behavior needs filesystem/error-injection coverage.
