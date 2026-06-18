<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.cc

## Purpose
Implements `TestUtils::TempDir`, an RAII helper that creates a temporary directory for tests and removes it recursively on destruction.

## Important APIs, Types, And Functions
The default constructor builds a mutable template from `path_`, calls `XPlatform::Syscall::CreateTempDir()`, asserts success with gtest, and stores the actual path. Copy/move assignment update `path_`; the destructor calls `std::filesystem::remove_all()`.

## Control Flow
Construction creates the temp directory before tests use it. Destruction exits early if initialization failed; otherwise it removes the directory tree and emits stderr diagnostics when removal fails.

## State And Persistence
State is `path_` and `is_path_init_`. Persistent filesystem state is temporary and intended to be deleted in the destructor.

## Dependencies And Integration Points
Depends on `utils/temp-dir.h`, `x-platform/syscall.h`, gtest assertions, and C++17 filesystem. Used by tests needing isolated directories.

## Risks
Move construction does not transfer `is_path_init_`, so a moved-to object may not clean up an initialized path while the moved-from object may clean an empty or moved path depending on string state. Copying can duplicate cleanup ownership.

## Test Signals
Signals are successful temp directory creation and absence of leftover temporary directories after tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.cc -->
