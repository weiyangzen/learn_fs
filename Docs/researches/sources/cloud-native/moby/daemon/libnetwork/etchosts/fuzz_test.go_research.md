# Research: sources/cloud-native/moby/daemon/libnetwork/etchosts/fuzz_test.go

Purpose: fuzzes `etchosts.Add` against arbitrary initial file bytes and generated record slices. Important entry point is `FuzzAdd`.

Control flow: the fuzzer consumes input bytes as initial file content, an integer record count, and up to 40 generated `Record` structs. It writes the bytes to a temp file and calls `Add`, ignoring the returned error. This is designed to find panics or data-race style crashes rather than assert semantic output.

State/dependencies: fuzz state is isolated per test temp directory and uses actual file writes. Dependencies include AdaLogics go-fuzz-headers, OS file IO, and the package `Record` type. Integration point is robustness of append formatting for arbitrary `netip.Addr`/host data. Risks covered include panics from malformed generated records or unusual initial content. Gaps include `Build`, `Delete`, and `Update` fuzzing, plus assertions about resulting file validity.
