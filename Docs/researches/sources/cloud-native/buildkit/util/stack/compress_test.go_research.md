<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/compress_test.go -->
# sources/cloud-native/buildkit/util/stack/compress_test.go

Purpose: tests stack compression behavior using nested errors with multiple stack traces.

Important APIs and types: helper functions `testcall1`, `testcall2`, `testcall3`, `TestCompressStacks`, and `TestCompressMultiStacks`.

Control flow: helpers create errors with stack wrapping at controlled call sites. Tests call `Traces`, assert number and length of resulting stack traces, check expected function names in leading frames, and verify shared suffix trimming.

State and persistence: no external state.

Dependencies and integration: uses `pkg/errors` for stack-bearing errors and `testify/require`.

Risks: assertions depend on function names and relative frame layout; compiler/runtime changes can affect exact stack depth but tests use greater-or-equal where needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/compress_test.go -->
