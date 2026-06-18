<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cap/cap_linux.go -->
# sources/cloud-native/containerd/pkg/cap/cap_linux.go

Purpose: Linux capability utilities for decoding kernel capability bitmaps and reading the current process capabilities from `/proc`.

Important APIs and types: `FromNumber`, `FromBitmap`, `Type` constants (`Inheritable`, `Permitted`, `Effective`, `Bounding`, `Ambient`), `ParseProcPIDStatus`, `Current`, `Known`, and capability lists by kernel vintage.

Control flow and state: `ParseProcPIDStatus` scans `/proc/<pid>/status`, recognizes `Cap*` fields, parses hex bitmaps, and returns a map by `Type`. `Current` reads `/proc/self/status`, decodes effective capabilities, and returns known names. `FromBitmap` iterates set bits, separates known capability names from unknown numbers, and masks only the latest known list.

Dependencies and integration: standard `bufio`, `io`, `os`, `strconv`, and capability knowledge embedded as static slices. Used by code that needs diagnostic or runtime capability reporting.

Risks and test signals: `Known` is fixed to kernel 5.9 capability names, so newer kernels can appear as unknown bits until updated. Fuzz tests cover proc-status parsing shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cap/cap_linux.go -->
