# sources/cloud-native/containerd/core/snapshots/storage/metastore_test.go

## Purpose
Provides a reusable behavioral test suite for snapshot metadata stores.

## APIs, Flow, State, Dependencies, Risks, And Tests
`MetaStoreSuite` registers tests for info lookup, empty/missing DB behavior, walk, active/view retrieval, create errors, commit errors, remove errors, parent ID ordering, and rebase behavior. Test wrappers create a temp metastore and run functions in read or write transactions. `basePopulate` creates committed, active, and view snapshots with parent relationships. Assertion helpers check errdefs categories. Individual tests validate kind/name/parent/timestamp/label equality, duplicate detection, parent must be committed, active commit preserves ID, views cannot commit, children block removal, parent IDs are ordered from immediate parent upward, and limited rebase is allowed only for parentless actives or unchanged parents.

State is temporary metastore data in real transactions. Dependencies include cmp, testify, errdefs, snapshots, context, and time.

Risks covered include inconsistent parent backlinks, wrong error categories, invalid commit/remove semantics, and broken timestamp handling. Gaps include process-crash tests and concurrent transaction tests. Passing this suite is the main correctness signal for a storage backend.
