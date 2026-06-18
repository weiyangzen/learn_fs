# sources/cloud-native/cri-o/contrib/metrics-exporter/dashboard.json

## Purpose
Grafana dashboard JSON for visualizing CRI-O Prometheus metrics per selected node.

## Important APIs, Types, and Functions
Dashboard inputs require Prometheus datasource; panels graph rates for container_runtime_crio_operations_total, operations_errors_total, and operations_latency_seconds_total_count; templating variable node is derived from container_runtime_crio_operations instance labels.

## Control Flow
Grafana imports JSON, user selects nodes, repeated panels query Prometheus over last 6h with configurable refresh intervals.

## State and Persistence
Dashboard itself is persisted by Grafana import; no application state beyond datasource and variable selection.

## Dependencies
Depends on Grafana schemaVersion 22, Prometheus datasource, and CRI-O metrics names/labels populated by the exporter/runtime.

## Integration Points
Complements metrics-exporter/cluster.yaml and main.go by consuming the instance labels generated in scrape configs.

## Risks and Edge Cases
Queries can break if metric names or labels change; latency panel uses a count-rate metric and may not represent duration; legacy Grafana panel schema may need migration.

## Test Signals
Import success and populated Prometheus queries are primary signals; empty node variable indicates scrape/exporter mismatch.
