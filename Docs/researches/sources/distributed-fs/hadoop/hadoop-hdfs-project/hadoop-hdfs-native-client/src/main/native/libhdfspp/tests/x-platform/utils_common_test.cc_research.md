<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_common_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_common_test.cc

## Purpose
Tests `XPlatform::Utils::Basename()` behavior for common, Unix-specific, or Windows-specific path forms.

## Important APIs, Types, And Functions
The tested API is `XPlatform::Utils::Basename`. Test cases are `XPlatformUtils.BasenameEmpty`, `XPlatformUtils.BasenameRelativePath`, `XPlatformUtils.BasenameSpecialFiles`.

## Control Flow
Each test passes a representative path string and compares the returned basename to the expected platform-specific value.

## State And Persistence
No state beyond local strings.

## Dependencies And Integration Points
Depends on gtest and `x-platform/utils.h`. These semantics are used by tools and tests that need portable path basename behavior.

## Risks
Platform-specific expectations can drift if path handling is changed to normalize more aggressively. Empty path and root path behavior are explicitly part of the contract.

## Test Signals
Passing tests indicate basename handling for empty paths, relative paths, dot entries, roots, trailing separators, and normal nested paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_common_test.cc -->
