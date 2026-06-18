# sources/control-plane/ceph-csi/internal/nfs/driver/driver.go

## Purpose
`driver.go` wires the NFS CSI driver process. It creates the CSI driver descriptor, registers capabilities, selects controller/node/identity servers, starts gRPC, and optionally enables profiling.

## Important APIs, Types, And Functions
`nfsDriver` implements `driver.Driver`. `NewDriver()` returns a new driver instance. `Run(conf)` is the main entrypoint.

## Control Flow And State
`Run()` creates a common CSI driver with driver name, version, node ID, instance ID, and fencing setting. Controller capabilities and volume access modes are added when running controller or combined mode. It builds a nonblocking gRPC server and always installs identity. Depending on config, it installs node, controller, or both servers, starts the gRPC server with middleware options, optionally starts metrics/profiling goroutines, and waits.

## State And Persistence Behavior
The file does not persist data itself. It initializes long-lived server objects and process-level gRPC/metrics/profiling state.

## Dependencies And Integration Points
It integrates common CSI server infrastructure, NFS controller/node/identity packages, driver config, feature gates, logging, and Prometheus/profiling helpers.

## Risks And Edge Cases
Mode selection uses a switch where node mode wins over controller mode if both booleans are true; combined mode is reached only when neither flag is set. Capability registration is skipped for pure node mode. Fatal logging exits the process on CSI driver initialization failure.

## Test Signals
No tests are present in this subset. Useful coverage would verify server selection, capability sets, node/controller combined behavior, profiling startup, and feature gate propagation.
