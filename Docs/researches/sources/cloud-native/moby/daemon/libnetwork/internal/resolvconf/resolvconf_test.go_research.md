# sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf_test.go

## Purpose
Specifies the expected behavior of resolv.conf parsing, mutation, transformation, rendering, and hash-based modification detection.

## Important APIs, Types, And Functions
- `TestRCOption` validates last-option-wins lookup and empty option values.
- `TestRCWrite` exercises `WriteFile` permissions, optional hash creation, and `UserModified`.
- `TestRCModify`, `TestRCTransformForLegacyNw`, `TestRCTransformForIntNS`, `TestRCInvalidNS`, `TestRCSetHeader`, and `TestRCUnknownDirectives` compare generated content against golden files.
- `TestRCTransformForIntNSInvalidNdots` checks malformed `ndots` replacement only when the internal resolver requires ndots.
- `TestRCRead` checks file loading, missing-file error propagation, and source-path inference from `os.File`.
- `TestRCParseErrors` asserts a stable message for scanner lines exceeding `bufio.MaxScanTokenSize`.
- `BenchmarkGenerate` measures rendering overhead with representative metadata.

## Control Flow
Tests construct resolv.conf snippets in memory, parse them, apply overrides or transforms, then inspect structured fields and rendered output. Golden-file tests are the primary regression signal for exact comments and directive ordering.

## State And Persistence
Temporary directories isolate file and hash writes. Golden files under the package testdata are external expectations. No daemon state is modified.

## Dependencies And Integration Points
Uses `gotest.tools`, `google/go-cmp`, Moby `sliceutil`, and golden files. The tests document expectations consumed by sandbox DNS generation and embedded resolver setup.

## Risks
Golden tests make deliberate output changes visible but can be brittle for harmless wording changes. The path-selection helper is not directly tested here. `TestRCWrite` has OS-specific permission behavior on Windows.

## Test Signals
Coverage is broad for parser/generator edge cases: invalid nameservers are warnings, unknown directives are preserved, search override drops `"."`, host-vs-override nameserver provenance affects `HostLoopback`, and overlong input becomes a system-style parse error.
