# sources/distributed-fs/lizardfs/src/unittests/TemporaryDirectory.h

Purpose: RAII helper that creates a unique temporary directory for tests and removes it recursively in the destructor.

Important APIs/types/functions: `TemporaryDirectory` constructor; destructor; `name()`.

Control flow: Constructor rejects comments containing `/`, builds a directory name from prefix, timestamp, microseconds, pid, and optional comment, then creates the directory. Destructor calls `boost::filesystem::remove_all` with ignored error code.

State and persistence: Creates real filesystem state for a test lifetime and deletes it on destruction. The directory name is stored in `name_`.

Dependencies and integration: Uses `boost::filesystem`, `boost::format`, `gettimeofday`, and `getpid`. Useful for tests needing isolated directories.

Risks and test signals: Constructor throws `new std::runtime_error`, which throws a pointer rather than an exception object. Directory creation errors are not checked. Destructor suppresses cleanup errors.
