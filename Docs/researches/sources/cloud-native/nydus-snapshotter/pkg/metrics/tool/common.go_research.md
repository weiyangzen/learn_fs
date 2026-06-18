# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/common.go

This file provides small numeric and system helpers for metrics. `FormatFloat64` rounds through formatted strings to either six or two decimal places. `ParseFloat64` parses strings and ignores errors. `GetClkTck` runs `getconf CLK_TCK`, falling back to 100 when unavailable or failing. `GetPageSize` returns `os.Getpagesize` as float64.

State is exposed through package globals in `stat.go` (`ClkTck` and `PageSize`) initialized from these helpers. Integration points include snapshotter and daemon CPU/memory resource collectors. Dependencies include OS commands, PATH lookup, logging, and strconv formatting.

Risks include ignored parse errors returning zero, shelling out to `getconf` at package initialization time, fallback assumptions for nonstandard platforms, and rounding by string conversion. There are no direct tests for these helpers; process stat tests indirectly rely on initialized globals.
