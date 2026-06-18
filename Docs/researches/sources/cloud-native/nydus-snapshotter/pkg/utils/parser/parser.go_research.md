<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser.go

Purpose: parses memory-size configuration strings into byte counts, including binary units and percentages.

Important APIs/state: `MemoryConfigToBytes(data string, totalMemoryBytes int)`, `InitUnitMultipliers`, and package globals `unitMultipliers` plus `sync.Once`. Supported units are `B`, `%`, and IEC suffixes `KiB/MiB/GiB/TiB/PiB` plus short forms `Ki/Mi/Gi/Ti/Pi`.

Control flow: empty string returns `-1`. A raw numeric string parses directly as bytes. Otherwise a regexp extracts a floating value and alphabetic/percent unit. Percentages are rounded with `+0.5` against `totalMemoryBytes`; known binary units multiply by the initialized map.

Dependencies/integration: uses regexp, strconv, sync, and pkg/errors. This feeds config parsing for resource limits or cache sizing.

Risks and test signals: unknown alphabetic units currently return multiplier zero without an error, yielding zero bytes. The regexp is not anchored, so strings with a valid prefix plus garbage can parse unexpectedly. `parser_test.go` covers valid empty, percent, raw, byte, and binary-unit cases, but not invalid/unknown units.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser.go -->
