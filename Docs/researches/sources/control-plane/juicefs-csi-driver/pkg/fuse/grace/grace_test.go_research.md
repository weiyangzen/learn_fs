# sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/grace_test.go

Purpose: tests parsing of graceful-upgrade socket request messages.

Important APIs and functions: `Test_parseRequest` checks a pod request with explicit action, a pod request defaulting to `noRecreate`, and a batch request containing `batchConfig` and `batchIndex`.

Control flow: each table entry calls `parseRequest` and compares the resulting `upgradeRequest` with `reflect.DeepEqual`.

State and persistence behavior: no state is persisted or mutated. It is a pure string parsing test.

Dependencies and integration points: depends on the constants in `grace.go`, `fmt`, `reflect`, and Go's `testing`.

Risks and test signals: confirms basic protocol parsing only. It does not test malformed batch options, invalid indexes, socket I/O, Kubernetes upgrade flows, or fd handoff.
