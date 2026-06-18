<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_common_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_common_test.cc

## Purpose
Tests x-platform syscall helper behavior for wildcard matching, secure buffer clearing, case-insensitive string comparison, temporary file/directory creation, and platform path separators.

## Important APIs, Types, And Functions
Tested functions include `XPlatform::Syscall::FnMatch`, `ClearBufferSafely`, `StringCompareIgnoreCase`, `CreateAndOpenTempFile`, `CloseFile`, and `CreateTempDir`. Test cases are `XPlatformSyscall.FnMatchBasicAsterisk`, `XPlatformSyscall.FnMatchBasicQuestionMark`, `XPlatformSyscall.FnMatchNegativeAsterisk`, `XPlatformSyscall.FnMatchNegativeQuestionMark`, `XPlatformSyscall.ClearBufferSafelyChars`, `XPlatformSyscall.ClearBufferSafelyNumbers`, `XPlatformSyscall.StringCompareIgnoreCaseBasic`, `XPlatformSyscall.StringCompareIgnoreCaseNegative`, `XPlatformSyscall.CreateAndOpenTempFileBasic`, `XPlatformSyscall.CreateAndOpenTempFileNegative`, `XPlatformSyscall.CreateTempDirBasic`, `XPlatformSyscall.CreateTempDirNegative`.

## Control Flow
Common tests run on every platform; `syscall_nix_test.cc` and `syscall_win_test.cc` add path separator specific wildcard behavior. Temp helpers mutate pattern buffers and return descriptors or booleans that are asserted.

## State And Persistence
Temporary files/directories may be created during tests; descriptors are closed. Buffers and strings are stack/local state.

## Dependencies And Integration Points
Depends on gtest and `x-platform/syscall.h`. It validates low-level wrappers used by temp utilities, directory tests, and path-matching logic.

## Risks
Temporary directory tests may leave directories if cleanup is not performed by the wrapper or OS. Wildcard semantics can differ between native APIs, so platform-specific tests guard separator behavior.

## Test Signals
Passing tests show consistent wildcard matching, zeroing, temp resource creation failure handling, and case-insensitive comparison across platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_common_test.cc -->
