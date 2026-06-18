# sources/control-plane/ceph-csi/internal/liveness/liveness.go

## Purpose
`liveness.go` implements the Ceph-CSI liveness sidecar logic. It probes the CSI driver over gRPC and exposes a Prometheus gauge indicating readiness.

## Important APIs, Types, And Functions
`liveness` is a Prometheus gauge named `csi_liveness`. `getLiveness(timeout, csiConn)` sends a CSI Probe RPC and updates the gauge. `recordLiveness(endpoint, drivername, pollTime, timeout)` registers metrics, connects to the CSI endpoint, and probes periodically. `Run(conf)` starts polling and the metrics server.

## Control Flow And State
`Run()` launches `recordLiveness()` in a goroutine and then starts the metrics HTTP server. `recordLiveness()` registers the gauge, opens a CSI connection using csi-lib-utils metrics manager, then loops on a ticker. Each probe uses a timeout-bound context. Probe errors or not-ready responses set the gauge to zero; ready responses set it to one.

## State And Persistence Behavior
State is process-local Prometheus metric state. There is no disk persistence. The gRPC connection is held for the life of the liveness process.

## Dependencies And Integration Points
The file uses Kubernetes CSI lib-utils `connection`, `metrics`, and `rpc`, Prometheus client, gRPC, and Ceph-CSI config/logging/metrics server helpers. It runs as an auxiliary liveness process for CSI components.

## Risks And Edge Cases
`prometheus.Register` failure is fatal, so duplicate registration in the same process kills liveness. `connlib.Connect` is expected to retry forever; a returned error is treated as fatal misconfiguration. The first gauge update does not occur until the first ticker tick.

## Test Signals
No tests are included in this subset. Useful tests would mock Probe responses, duplicate registration, connection failure, timeout behavior, and gauge updates.
