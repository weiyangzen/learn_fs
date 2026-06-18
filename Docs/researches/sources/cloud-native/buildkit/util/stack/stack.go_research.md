<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.go -->
# sources/cloud-native/buildkit/util/stack/stack.go

Purpose: captures, wraps, extracts, compresses, and formats BuildKit stack traces, including conversion from `pkg/errors` stack frames into protobuf `Stack` objects.

Important APIs and types: `SetVersionInfo`, `Helper`, `Traces`, `Enable`, `Wrap`, `Formatter`, `convertStack`, `withStackError`, and package-level helper registry.

Control flow: `Enable` records its caller as a helper and adds a stack only if the error chain lacks a local `pkg/errors` stack trace. `Traces` recursively unwraps single or multi-error chains, extracts `pkg/errors.StackTrace` and BuildKit `*Stack` traces, then compresses them. `Formatter` prints normal error text, or with `%+v`, includes pid, version, command line, and frames.

State and persistence: package globals track version/revision and helper function names protected by a mutex. Stack objects record command line and pid at conversion time.

Dependencies and integration: registers `Stack` with containerd `typeurl`, uses `pkg/errors`, runtime frame APIs, process args, and generated protobuf types.

Risks: helper filtering relies on function names recorded by `Helper`; misuse can hide frames. `hasLocalStackTrace` checks only single unwrap chains, not multi-error chains. Formatting may expose command-line arguments.

Test signals: compression tests exercise `Traces` and stack frame conversion indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.go -->
