## sources/cloud-native/soci-snapshotter/benchmark/parser/main.go

Purpose: command-line helper that scans a benchmark log and groups JSON benchmark events by test UUID and benchmark event name.

Important APIs/types/functions: `BenchmarkEvent` maps expected JSON fields, `ProfileEvent` stores start/stop timestamps, `BenchmarkProfile` groups events for one test, `parseLogLineToMap` updates the map, and `printLogMap` dumps the collected profile.

Control flow: `main` opens `os.Args[1]`, scans line by line, filters lines containing `benchmark`, unmarshals JSON, records `Start` and `Stop` times using RFC3339 parsing, then prints the map.

State and persistence: all parsed state is in memory; output is printed to stdout. It reads one log file but does not write files.

Dependencies and integration: depends only on standard library packages and the benchmark framework's JSON log shape.

Risks and test signals: argument count, JSON unmarshal errors, and time parse errors are ignored, so malformed input can silently produce zero timestamps. There are no tests in this subset for this parser.
