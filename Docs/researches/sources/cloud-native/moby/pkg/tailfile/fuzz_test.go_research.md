# sources/cloud-native/moby/pkg/tailfile/fuzz_test.go

Purpose: fuzz harness for the tailfile reader.

APIs and flow: consumes fuzz bytes into a requested line count and file contents, writes those bytes to a temp file, seeks to the beginning, and calls `TailFile` with the generated count.

State and dependencies: creates temporary files per fuzz case; depends on AdaLogics go-fuzz-headers for structured byte consumption.

Integration points: targets panic/error-safety around reverse scanning and arbitrary input sizes/content.

Risks and signals: the harness discards most setup errors and does not assert semantic output, so its value is crash discovery rather than correctness.
