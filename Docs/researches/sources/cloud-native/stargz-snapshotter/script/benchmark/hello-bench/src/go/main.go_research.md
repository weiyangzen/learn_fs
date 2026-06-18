# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/go/main.go

Purpose: Tiny Go workload used by the Go benchmark image.
Important APIs/types/functions: `main` prints `hello` with `fmt.Println`.
Control flow: run by `go run main.go` from `hello.py` inside the `golang:1.18` container.
State and persistence: no persistent state.
Dependencies and integration points: depends on bind-mounted source and Go toolchain in the image.
Risks: only measures toolchain/container startup, not application complexity.
Test signals: benchmark succeeds when `go run` exits zero.
