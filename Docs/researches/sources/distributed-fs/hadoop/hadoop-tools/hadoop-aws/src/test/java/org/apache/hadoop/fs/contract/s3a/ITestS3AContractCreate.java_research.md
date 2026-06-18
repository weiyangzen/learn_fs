# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractCreate.java

Purpose: S3A file-create contract tests across normal create mode and create performance mode.

Important APIs/types/functions: extends `AbstractContractCreateTest`, parameterized by `createPerformance` and `expectContinue`. `createConfiguration()` sets performance flags, clears `CONNECTION_EXPECT_CONTINUE`, toggles 100-continue, skips performance mode unless enabled, and disables FS caching.

Control flow: overwrite/error tests invoke superclass behavior, but in create performance mode expected assertion failures are swallowed; if they pass unexpectedly, `failWithCreatePerformance()` fails the test.

State and persistence: creates and overwrites S3 paths through inherited contract tests; no static state.

Dependencies and integration: uses `S3AContract`, `S3ATestUtils.setPerformanceFlags`, performance-test enable flags, and S3A connection options.

Risks: deliberately changes expected behavior under create performance mode, where overwrite conflict detection may be relaxed for speed. Parameter set only covers `{false,false}` and `{true,true}` combinations.

Test signals: parameterized integration coverage of create semantics and expected-continue interaction.
