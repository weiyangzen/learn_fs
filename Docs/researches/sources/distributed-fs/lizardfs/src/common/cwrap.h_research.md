# sources/distributed-fs/lizardfs/src/common/cwrap.h

Purpose: declares RAII wrappers and filesystem helper functions around C/POSIX resources.

Important APIs/types/functions: `FileDescriptor` is non-copyable and owns an integer fd. `CFileCloser`, `CDirCloser`, `cstream_t`, and `cdirectory_t` provide unique-pointer ownership for `FILE*` and `DIR*`. `errorString` and namespace `fs` expose existence, rename, remove, dirname, and cwd helpers.

Control flow: callers use wrappers to convert errno-producing C APIs into exceptions or RAII cleanup.

State and persistence: only owned descriptors/handles; filesystem effects are delegated to implementation.

Dependencies and integration: includes `dirent.h`, `sys/types.h`, `<cstdio>`, `<memory>`, and `<string>`. Used by common code that needs portable cleanup and consistent error reporting.

Risks: the documentation for `fs::exists` says "True iff given file does not exists", but implementation returns true when it exists. The API does not expose close error status.

Test signals: no direct tests in this subset.
