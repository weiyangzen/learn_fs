# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/types_test.go

Purpose: focused regression test for deep copying `StringOrStringSlice` values.

Important APIs and functions: `TestCloneStringOrStringSliceCopiesBackingSlice` calls `NewStringOrStringSlice` and `CloneStringOrStringSlice`.

Control flow: creates an original two-action slice, clones it, mutates the clone's backing slice, then asserts the original remains unchanged while the clone reflects the mutation.

State and persistence: no external state.

Dependencies and integration: protects the clone behavior used when compiling policies and copying statement fields.

Risks: the test reaches the unexported `values` field because it is in the same package. External callers still cannot mutate internals directly, but package-local code can.

Test signals: narrow but important immutability signal for compiled policy safety.
