<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/errdefs/file.go -->
## sources/cloud-native/buildkit/solver/llbsolver/errdefs/file.go

Purpose: annotates file-operation errors with the index of the failing file action.

Important APIs and types: `FileActionError`, `WithFileActionError`, and `ToSubject`.

Control flow: `WithFileActionError` returns nil for nil errors and otherwise wraps the cause with an action index. `ToSubject` converts the index into solver errdefs `Solve_File` subject detail so solve errors can identify the failing action.

State and dependencies: no persistence; only stores index and error. Depends on top-level solver errdefs package.

Integration points: file op solver/backend paths can wrap action failures and then `WithSolveError` can serialize the subject into typed gRPC details.

Risks and test signals: correctness depends on callers using the same action index as the LLB `FileAction` list. No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/errdefs/file.go -->
