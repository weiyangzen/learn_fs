# Research: sources/cloud-native/containerd/cmd/containerd-stress/size.go

## Purpose
Records binary size metrics for selected containerd executables when the stress metrics server is enabled.

## Important APIs, Control Flow, And State
`binaries` lists default binary names under `/usr/local/bin/`. `checkBinarySizes` stats each path and updates `binarySizeGauge` with byte sizes, logging warnings when stat fails. It reads local filesystem metadata and mutates only the metrics registry.

## Dependencies And Integration
Uses `os.Stat`, logging, and the `binarySizeGauge` defined in `main.go`. Called by `serve` before running stress mode with metrics.

## Risks And Test Signals
Risks include hard-coded install path assumptions and missing binaries producing noisy warnings. Tests should cover gauge updates for temp files and warning behavior for absent files; configuration could be added if alternate install paths matter.
