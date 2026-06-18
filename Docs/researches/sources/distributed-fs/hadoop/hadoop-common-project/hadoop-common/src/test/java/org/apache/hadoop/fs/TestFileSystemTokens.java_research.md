## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemTokens.java

Purpose: verifies `FileSystem.addDelegationTokens` behavior for filesystems with no token, own token, existing credentials, child filesystems, duplicate children, nested filters, and duplicate service names.

Important APIs/types/functions: `FileSystemTestHelper.MockFileSystem`, `FileSystem.addDelegationTokens`, `getCanonicalServiceName`, `getDelegationToken`, `getChildFileSystems`, `Credentials`, `Token`, `Text`, `FilterFileSystem`, Mockito answers, and helper `verifyTokenFetch`.

Control flow: each test creates mock filesystems with configured service names and child relationships, invokes `addDelegationTokens`, verifies whether token fetches occurred, and asserts credential token counts/services. The deepest test builds nested duplicate children and filtered filesystems to ensure deduplication recurses correctly without fetching tokens already present.

State and persistence: all state is in-memory mocks and `Credentials`. Tokens created in answers have their service set to the requested `Text`.

Dependencies/integration points: protects Hadoop security credential collection for composite filesystems and filters. It ensures callers avoid duplicate token requests and preserve existing credentials.

Risks and test signals: regressions can over-fetch tokens, miss child tokens, or replace existing tokens. The test verifies canonical service lookup is always performed and child traversal occurs even when the current FS has no token.
