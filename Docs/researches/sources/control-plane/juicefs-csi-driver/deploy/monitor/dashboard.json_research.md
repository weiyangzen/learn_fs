<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/monitor/dashboard.json -->
# sources/control-plane/juicefs-csi-driver/deploy/monitor/dashboard.json

## Purpose
Grafana dashboard JSON for monitoring JuiceFS CSI driver health and operation errors.

## Important APIs, Types, and Resources
Defines dashboard `JuiceFS CSI Driver`, schema version 41, 30s refresh, datasource template variable, stat panels for node readiness/controller availability/mount points/error counters, timeseries panels for volume path health and error rates, and a table for volume health details. PromQL expressions reference kube-state-metrics and JuiceFS metrics such as `juicefs_volume_path_health`, `juicefs_provision_errors`, `juicefs_volume_errors`, and `juicefs_volume_del_errors`.

## Control Flow
Grafana loads the JSON, resolves the Prometheus datasource, and executes panel queries over the last hour by default. Operators use stat panels for current health and timeseries/table panels to drill into node-level or volume-level failures.

## State and Persistence
The JSON stores dashboard definition only. Runtime state lives in Grafana's dashboard store and Prometheus time series; no metrics are persisted by this file.

## Dependencies and Integration Points
Depends on Grafana dashboard schema, Prometheus datasource availability, kube-state-metrics names for DaemonSet/StatefulSet readiness, and CSI driver metric names. Integrates with monitoring documentation and cluster observability setup.

## Risks
Risks are metric-name drift, missing kube-state-metrics, fixed resource names that do not match customized installs, and dashboard JSON schema drift in future Grafana versions.

## Test Signals
Import the dashboard into Grafana, run Prometheus query validation, confirm non-empty panels on a live cluster, and compare panel queries with current driver metric names.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/monitor/dashboard.json -->
