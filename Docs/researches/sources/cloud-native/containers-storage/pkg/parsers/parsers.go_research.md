# sources/cloud-native/containers-storage/pkg/parsers/parsers.go

Purpose: provides generic string parsers for key/value options and unsigned integer/range lists used by cgroup-style files.

Important APIs, types, and functions: `ParseKeyValueOpt` and `ParseUintList`.

Control flow: `ParseKeyValueOpt` splits on the first `=`, trims spaces around key and value, and errors if no separator exists. `ParseUintList` splits comma-separated entries, accepts single integers and `min-max` ranges, validates numeric conversion and range order, and marks every included integer in a map.

State and persistence: no state or persistence; functions return parsed values.

Dependencies and integration points: depends on `fmt`, `strconv`, and `strings`. Useful for cgroup cpuset/memory parser call sites.

Risks and edge cases: despite the name, `ParseUintList` uses `strconv.Atoi` and therefore accepts negative single integers unless rejected by format in tests; `-1` fails because it is parsed as a malformed range due to `strings.Cut`. Large ranges can allocate huge maps and loop extensively.

Test signals: `parsers_test.go` covers trimming, values containing `=`, empty input, duplicate/overlap ranges, leading zeros, reverse ranges, malformed separators, and invalid tokens.
