<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.cc

## Purpose
Implements `TestUtils::TempFile`, an RAII helper that creates a temporary file, tracks its descriptor and filename, closes it, and unlinks it on destruction.

## Important APIs, Types, And Functions
The default constructor calls `XPlatform::Syscall::CreateAndOpenTempFile()` on a mutable filename template. The alternate constructor wraps an existing filename without opening it. Copy/move assignment copy the filename and descriptor. The destructor calls `XPlatform::Syscall::CloseFile()` when `fd_ != -1` and then `unlink()`.

## Control Flow
Construction creates or records the file. Tests obtain the name through `GetFileName()`. Destruction closes the descriptor and removes the path.

## State And Persistence
State is `filename_` plus `fd_`. Persistent local filesystem state exists only for the helper lifetime, assuming destructor cleanup succeeds.

## Dependencies And Integration Points
Depends on `utils/temp-file.h`, x-platform syscall helpers, gtest assertions, and POSIX-style `unlink`.

## Risks
Copying duplicates the raw file descriptor value and can cause double-close. Move construction does not invalidate the source descriptor, so moved objects also risk double-close. The explicit filename constructor unlinks the path even when it did not open it.

## Test Signals
Signals are successful temp-file creation, valid descriptors, successful close, and no leftover files after tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.cc -->
