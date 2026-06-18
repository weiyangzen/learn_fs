# sources/distributed-fs/ipfs-kubo/test/cli/testutils/cids.go

Purpose: centralizes well-known CID string constants used by CLI tests.

Important APIs: `CIDWelcomeDocs` stores the welcome docs CID and `CIDEmptyDir` stores the empty directory CID.

Control flow: no executable code; constants are imported by tests that need stable CIDs.

State and persistence: no state. The values are stable external identifiers.

Dependencies and integration points: `CIDEmptyDir` is used by routing/offline tests as a syntactically valid CID argument. Other test files can import these constants through dot imports from `testutils`.

Risks and test signals: changing these constants affects many tests and should only happen when fixture assumptions change. Invalid or deprecated CIDs would cause unrelated command validation tests to fail for the wrong reason.
