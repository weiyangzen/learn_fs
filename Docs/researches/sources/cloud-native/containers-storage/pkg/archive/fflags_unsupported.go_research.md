<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/fflags_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/archive/fflags_unsupported.go

Purpose: non-FreeBSD no-op implementation of file flag preservation hooks.

Important APIs/types/functions: `ReadFileFlagsToTarHeader`, `WriteFileFlagsFromTarHeader`, and `resetImmutable`.

Control flow: all functions return nil and do not inspect their inputs.

State/persistence: none.

Dependencies/integration: keeps archive extraction and tar creation call sites platform-neutral. On unsupported platforms, `diff.go` can call `resetImmutable` without conditional code.

Risks/test signal: platforms using this file do not preserve BSD-style flags and cannot clear immutable flags through this abstraction. Behavior is intentional and covered mostly by compile-time portability plus non-BSD layer tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/fflags_unsupported.go -->
