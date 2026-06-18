<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/metrics.go -->
# sources/cloud-native/moby/daemon/command/metrics.go

## Purpose
Starts the daemon Prometheus-style metrics HTTP endpoint when configured.

## Important APIs, Types, And Functions
`startMetricsServer` validates the address, reserves the daemon port, listens on TCP, registers `/metrics` with `go-metrics`, and runs `http.Server.Serve` in a goroutine.

## Control Flow
Empty address is a no-op. Non-empty address must pass `allocateDaemonPort` and `net.Listen`; serving errors other than listener closure are logged.

## State And Persistence Behavior
Creates a live TCP listener and goroutine. No shutdown handle is returned, so lifecycle is tied to process/listener closure.

## Dependencies And Integration Points
Depends on libnetwork port reservation, Go HTTP, containerd logging, and Docker metrics registry handler.

## Risks And Test Signals
Risks include untracked goroutine lifetime, long read-header timeout, and metrics port conflicting with published container ports if reservation fails. Integration signal is `/metrics` availability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/metrics.go -->
