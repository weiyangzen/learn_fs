# sources/cloud-native/cri-o/contrib/metrics-exporter/Containerfile

## Purpose
Minimal container image definition for the metrics exporter binary.

## Important APIs, Types, and Functions
FROM scratch, COPY bin/metrics-exporter /metrics-exporter, ENTRYPOINT /metrics-exporter.

## Control Flow
Build output must place a statically runnable metrics-exporter at bin/metrics-exporter; container starts the binary directly.

## State and Persistence
No mutable state in image; runtime state is whatever the binary writes to Kubernetes ConfigMaps or serves over HTTP.

## Dependencies
Depends on container build context containing bin/metrics-exporter and on the binary being suitable for scratch.

## Integration Points
Used with cluster.yaml Deployment image quay.io/crio/metrics-exporter:latest.

## Risks and Edge Cases
No shell, CA bundle, or debug tooling in scratch image; binary must include all runtime needs. Tagging latest in deployment can obscure provenance.

## Test Signals
No direct tests; successful build/run and exporter HTTP readiness are the practical signals.
