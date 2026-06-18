# sources/cloud-native/containerd/core/content/testsuite/testsuite.go

Purpose: reusable conformance suite for `content.Store` implementations.

Important APIs/functions: `StoreInitFn` initializes stores for tests. `ContentSuite` runs core writer/status/resume/blob/label/error-state tests. Cross-namespace suites validate shared and isolated content policies. `ContextWrapper`, `SetContextWrapper`, and `Name` support namespace/lease decoration. Helpers include `checkContentStoreWriter`, `checkResumeWriter`, `checkCommitExists`, `checkCommitErrorState`, `checkUpdateStatus`, `checkLabels`, resume strategies, cross-namespace checks, `checkStatus`, `checkInfo`, `checkContent`, and deterministic `createContent`.

Control flow and state: `makeTest` creates a temp root, initializes the store, optionally wraps context, registers cleanup, and dumps temp content on failure. Tests write deterministic random content, check writer status/digest/timestamps, reopen refs, verify commit errors preserve state, mutate labels, and assert cross-namespace visibility rules.

Dependencies and integration: core content helpers/interfaces, `testutil.DumpDirOnFailure`, errdefs, logtest, OCI descriptors, go-digest, testify.

Risks: timestamp assertions are relaxed on Windows. Some expectations are intentionally skipped/commented where implementations do not guarantee `Status.Expected`. Large blob test writes `16 << 21` bytes, so slow stores need capacity.

Test signals: very strong behavioral contract for local and remote content stores, especially resumability, lock/unavailable refs, commit failure recovery, labels, and namespace policy.
