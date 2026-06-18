# sources/cloud-native/containers-storage/pkg/regexp/regexp.go

Purpose: wraps Go regular expressions so global regex variables can be lazily compiled, reducing startup cost unless a build tag requests precompilation.

Important APIs, types, and functions: `Regexp`, `Delayed`, private `regexpStruct`, `compile`, wrapper methods for most `regexp.Regexp` operations, and `noCopy`.

Control flow: `Delayed` stores the pattern and optionally compiles immediately when `precompile` is true. Every method calls `compile`, which uses `sync.Once` to compile lazily when not precompiled, then delegates to the embedded `regexp.Regexp`.

State and persistence: in-memory compiled regex cache per `Regexp`. No persistence.

Dependencies and integration points: depends on `io`, stdlib `regexp`, and `sync`. Used by string/id validation and any package wanting delayed global regexes.

Risks and edge cases: invalid regex patterns panic at first use, not declaration time, unless precompiled. `Longest` mutates regex matching behavior after compile. Copying after use is discouraged through `noCopy` vet signaling but not runtime-enforced.

Test signals: `regexp_test.go` covers interface compatibility, `MatchString`, and `FindStringSubmatch`.
