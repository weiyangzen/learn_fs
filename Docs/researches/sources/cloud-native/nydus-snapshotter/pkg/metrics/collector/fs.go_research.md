# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/fs.go

This file collects filesystem and inflight IO metrics from nydusd API payloads. `FsMetricsCollector` maps total read bytes, read hits, read errors, and custom histograms into Prometheus metrics. `FsMetricsVecCollector` clears histogram state before collecting a vector. `InflightMetricsVecCollector` counts hung IOs whose elapsed time exceeds a configured interval.

Important dependencies are `types.FsMetrics`, `types.InflightMetrics`, metric definitions in `data`, histogram utilities in `metrics/types`, and log output for invalid histogram shapes. `OPCodeMap` currently names only opcode 15 as `OP_READ`.

State is metric state plus temporary collector slices. Integration points include `metrics.Server.CollectFsMetrics` and `CollectInflightMetrics`, which poll running fusedev daemons. Risks include indexing `FopHits[mtypes.Read]` and `FopErrors[mtypes.Read]` without length checks, returning early if any histogram fails, clearing all histogram state before vector collection, and wall-clock dependence for hung IO classification. There are no direct unit tests here; histogram behavior is covered in `metrics/types`.
