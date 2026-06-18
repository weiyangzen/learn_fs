<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cap/cap_linux_test.go -->
# sources/cloud-native/containerd/pkg/cap/cap_linux_test.go

Purpose: tests and fuzzing for Linux capability name/bitmap/proc-status parsing.

Important APIs and functions: `TestCapsList`, `TestFromNumber`, `TestFromBitmap`, `TestParseProcPIDStatus`, `TestCurrent`, `TestKnown`, and `FuzzParseProcPIDStatus`.

Control flow and state: table tests verify capability list lengths and bitmap decoding across kernel capability vintages. A fixture `/proc/<pid>/status` string validates parsed `CapInh`, `CapPrm`, `CapEff`, `CapBnd`, and `CapAmb` values. `TestCurrent` reads live `/proc/self/status`.

Dependencies and integration: uses testify assertions and the real procfs for current process coverage.

Risks and test signals: live `TestCurrent` depends on Linux procfs availability. Fuzzing asserts parser never returns both a non-nil result and error for arbitrary inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cap/cap_linux_test.go -->
