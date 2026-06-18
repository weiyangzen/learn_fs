<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolvconf/resolvconf_test.go -->
# sources/cloud-native/buildkit/util/resolvconf/resolvconf_test.go

Purpose: comprehensive unit coverage for the resolv.conf parser, mutators, transforms, generator comments, invalid input handling, and benchmark performance.

Important APIs and types: `TestRCOption`, `TestRCModify`, `TestRCTransformForLegacyNw`, `TestRCTransformForIntNS`, `TestRCTransformForIntNSInvalidNdots`, `TestRCRead`, `TestRCInvalidNS`, `TestRCSetHeader`, `TestRCUnknownDirectives`, `BenchmarkGenerate`, and helper `sliceutilMapper`.

Control flow: tests construct input files with strings or temp files, call parse/load/mutator/transform methods, then assert generated content and exposed slices. Internal resolver tests also compare returned `ExtDNSEntry` values including `HostLoopback` semantics.

State and persistence: temporary filesystem use is limited to `TestRCRead`; all other tests are in memory.

Dependencies and integration: uses `net/netip`, `os`, `filepath`, string builders, and `testify` assertions. Test data documents intended generated comment format.

Risks: expected output strings are exact, so harmless formatting changes require coordinated updates. Tests cover many DNS paths but do not exercise concurrent use; `ResolvConf` is mutable and not designed as thread-safe.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolvconf/resolvconf_test.go -->
