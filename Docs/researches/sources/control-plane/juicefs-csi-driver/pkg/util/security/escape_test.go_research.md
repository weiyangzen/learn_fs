<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/security/escape_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/security/escape_test.go

### Purpose
`escape_test.go` verifies `EscapeBashStr` by comparing expected strings and executing them through bash to confirm round-trip output.

### Important APIs, Types, And Functions
The test covers `EscapeBashStr` and indirectly `containsOne`. It uses `exec.Command("bash", "-c", fmt.Sprintf("echo %s", escaped))` and trims output with `strings.TrimSpace`.

### Control Flow
For each case, the test checks the exact escaped representation, then runs `echo <escaped>` in bash. If the command succeeds, it compares the trimmed output with the original input.

### State, Persistence, And Dependencies
No repository state is changed. The test depends on a local `bash` binary and the host shell behavior for ANSI-C quoting. It does not use Kubernetes.

### Integration Points
This test is a safety net for mount/auth command generation that must preserve literal values containing shell injection syntax.

### Risks
The test itself uses `echo`, which can have portability quirks for backslash-like content, though bash built-in behavior is stable enough for these cases. `TrimSpace` hides leading/trailing whitespace changes. The test does not cover whitespace-only splitting because the helper intentionally leaves strings without listed metacharacters unquoted.

### Test Signals
Covered signals include unchanged safe strings, command substitution and backtick strings being quoted, embedded single quotes, pre-existing backslashes, nested `$'...'` text, and bash round-trip output matching the original value.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/security/escape_test.go -->
