# sources/cloud-native/containers-storage/tests/tools/tools.go

Purpose: Go tools pin file for test tooling. The `tools` build tag keeps tool dependencies in module metadata without compiling them into normal binaries.

Important APIs and control flow: it declares package `tools` and blank-imports `github.com/cpuguy83/go-md2man` and `github.com/vbatts/git-validation`. There are no runtime functions.

State and persistence: no runtime state. Its persistence effect is through `go.mod`, `go.sum`, and `vendor/`, because Go treats the imports as module requirements when the `tools` tag is considered.

Dependencies and integration: paired with `tests/tools/Makefile`, which builds the vendored tools. The file depends on Go build constraints to exclude it from ordinary builds.

Risks: tool versions are controlled indirectly by module resolution; if `go mod tidy` is run without respecting the tools pattern, dependencies can be dropped.

Test signals: `make vendor` and `go mod verify` confirm the tool imports remain resolvable and vendorable.
