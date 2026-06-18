# sources/cloud-native/containers-storage/pkg/regexp/regexp_precompile.go

Purpose: build-tag configuration that forces regex compilation during `Delayed`.

Important APIs, types, and functions: constant `precompile = true`.

Control flow: no runtime flow here; `regexp.go` uses the constant to compile in `Delayed` and skip lazy compile.

State and persistence: no persistence. Compiled regex state is created eagerly.

Dependencies and integration points: selected with build tag `regexp_precompile`. Useful when startup failures for invalid regexes are preferred over lazy runtime panics.

Risks and edge cases: increases startup work for global regex declarations but catches invalid patterns earlier.

Test signals: no explicit tagged test in the requested files; the same `regexp_test.go` should pass under either tag.
