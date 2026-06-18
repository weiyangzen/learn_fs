<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/security/escape.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/security/escape.go

### Purpose
`escape.go` provides a small shell-escaping helper for values inserted into bash command lines, focused on characters that can trigger command substitution, command chaining, redirection, or pipelines.

### Important APIs, Types, And Functions
`EscapeBashStr(s)` returns the original string when no risky characters are present, otherwise escapes backslashes and single quotes and wraps the value in ANSI-C `$'...'` quoting. `containsOne` checks whether a string contains any rune from a provided set.

### Control Flow
`EscapeBashStr` checks for `$`, backtick, `&`, `;`, `>`, `|`, `(`, or `)`. When found, it doubles backslashes, escapes single quotes as `\'`, and formats the result as `$'<escaped>'`. Strings without those characters are left unquoted.

### State, Persistence, And Dependencies
There is no persistent state. Dependencies are only `fmt` and `strings`. The helper is intended for command construction in JuiceFS mount/auth flows where user-controlled secrets or URLs may appear in shell text.

### Integration Points
Builder code that creates shell commands can use this helper to reduce injection risk for meta URLs, access keys, and other configuration values that are passed through `/bin/sh` or `bash`.

### Risks
The risky-character list is intentionally narrow and does not quote whitespace, glob characters, newlines, braces, or other shell metacharacters. `$'...'` is bash-specific; shells without ANSI-C quoting will not behave the same. Escaping only happens when a listed character appears, so a value containing spaces can still be split if inserted into an unquoted command position.

### Test Signals
Tests should validate round-trip shell interpretation, command-substitution suppression, quote/backslash escaping, and behavior for whitespace-only risky values if callers rely on preserving a single argument.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/security/escape.go -->
