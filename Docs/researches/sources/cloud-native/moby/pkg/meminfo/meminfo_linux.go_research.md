<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_linux.go -->
# sources/cloud-native/moby/pkg/meminfo/meminfo_linux.go

Purpose: Linux implementation of memory info parsing from `/proc/meminfo`. Important APIs are `readMemInfo` and `parseMemInfo`. Control flow scans key-value-unit lines, accepts `kB` units, parses integers, multiplies to bytes, and fills known `Memory` fields while ignoring malformed or unknown lines. State is read-only host procfs data. Dependencies are bufio, os, strconv, and strings. Risks include unit assumptions, malformed kernel output, zero values for missing keys, and scanner limitations. Test signal is `meminfo_unix_test.go` fixture parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_linux.go -->
