<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.h

## Purpose
Declares `TestUtils::TempDir`, a test RAII wrapper around a temporary directory rooted by default under `/tmp`.

## Important APIs, Types, And Functions
Public API includes default construction, copy/move constructors and assignment, `GetPath()`, and destructor cleanup. Private state is a path template string and an initialization flag.

## Control Flow
Consumers construct a `TempDir`, use `GetPath()` to create files under it, and rely on the destructor to recursively delete the directory tree.

## State And Persistence
The object owns a temporary filesystem path while alive. Cleanup is best effort through the implementation file.

## Dependencies And Integration Points
The header is standalone except for `<string>` and is implemented by `temp-dir.cc` using x-platform temp-directory creation.

## Risks
Defaulted copy construction can create multiple owners for the same directory path, while move handling needs careful ownership semantics. Tests should avoid copying unless duplicate cleanup is acceptable.

## Test Signals
Compilation of tests using `GetPath()` and clean teardown of temporary directories validate the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.h -->
