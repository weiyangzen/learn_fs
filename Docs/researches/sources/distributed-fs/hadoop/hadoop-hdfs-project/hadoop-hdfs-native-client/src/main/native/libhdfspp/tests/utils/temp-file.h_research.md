<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.h

## Purpose
Declares `TestUtils::TempFile`, a test helper that owns a temporary file path and, normally, an open descriptor.

## Important APIs, Types, And Functions
Public API includes default construction, construction from a filename, copy/move constructors and assignments, `GetFileName()`, and destructor cleanup. Private fields are `filename_` and `fd_`.

## Control Flow
Tests instantiate the helper, pass `GetFileName()` to code under test, and rely on destruction to close/unlink the file.

## State And Persistence
The object owns temporary local filesystem state while alive. Persistence is meant to end when the destructor runs.

## Dependencies And Integration Points
Implemented by `temp-file.cc` using `XPlatform::Syscall` temp-file and close wrappers.

## Risks
Copy and move declarations expose raw descriptor ownership hazards unless implementation invalidates moved/copied sources, which it currently does not.

## Test Signals
Successful helper construction and cleanup are the main signals; sanitizer or OS-level double-close diagnostics would reveal ownership bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.h -->
