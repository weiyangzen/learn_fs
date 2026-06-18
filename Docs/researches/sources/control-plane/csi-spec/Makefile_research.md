# sources/control-plane/csi-spec/Makefile

## Purpose

The top-level CSI spec Makefile extracts `csi.proto` from `spec.md`, builds C++ and Go bindings, and checks basic proto formatting constraints.

## Important Targets and Flow

`all` maps to `build`. `$(CSI_PROTO)` depends on `spec.md` and `Makefile`; it writes a generated-code header and extracts the fenced `protobuf` block from `spec.md` with `sed`. `build` runs `check`, `build_cpp`, and `build_go`. `build_cpp` delegates to `lib/cxx`. Go binding build delegates to `lib/go`, then downloads modules, installs/builds `./lib/go/csi`, and emits `csi.a`. `clean` removes `csi.a` and delegates cleanup; `clobber` also removes generated `csi.proto`. `check` runs an awk line-length check on the newly generated proto.

## State, Dependencies, and Integration

Generated state includes `csi.proto`, Go generated files, and `csi.a`. Dependencies are Make, sed, awk, Go modules, and subdirectory Makefiles. It integrates the human-readable spec with generated language APIs and the GitHub Actions build workflow.

## Risks and Test Signals

The proto extraction depends on exact Markdown fence markers. The `check` target only checks `$?`, so it primarily evaluates files newer than the target in the current make invocation. Test signals are successful `make`, clean generated diffs, and generated binding compilation.
