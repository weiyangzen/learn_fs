# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/expect.h

## Purpose
Assertion macro library for native libhdfs and FUSE C tests.

## Important APIs, Types, And Functions
Macros include `EXPECT_ZERO`, `EXPECT_NULL`, `EXPECT_NULL_WITH_ERRNO`, `EXPECT_NONNULL`, errno/integer comparison helpers, `ASSERT_INT64_EQ`, `EXPECT_STR_CONTAINS`, and `RETRY_ON_EINTR_GET_ERRNO`. Declares `expectFileStats`.

## Control Flow
Most macros evaluate an expression, print a diagnostic with `__FILE__`, `__LINE__`, errno, and expected value, then return an error from the enclosing function on failure. `ASSERT_INT64_EQ` exits the process.

## State, Persistence, And Dependencies
Macros rely on `errno` being meaningful immediately after expression evaluation. They do not persist state, but they control function returns.

## Integration Points
Used throughout native C tests including FUSE workload and libhdfs tests.

## Risks
Expression arguments with side effects are evaluated once in most macros but some macros reference string arguments more than once. Immediate returns can skip caller cleanup unless tests structure cleanup carefully. `RETRY_ON_EINTR_GET_ERRNO` expects POSIX `-1` failure style.

## Test Signals
Clear stderr diagnostics from these macros are the main native test failure signal.
