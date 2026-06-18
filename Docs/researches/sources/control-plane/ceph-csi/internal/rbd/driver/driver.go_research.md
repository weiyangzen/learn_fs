# sources/control-plane/ceph-csi/internal/rbd/driver/driver.go

## Purpose
Bootstraps the RBD CSI driver process. It initializes global RBD settings and journals, constructs identity/controller/node servers, advertises CSI capabilities, starts the main non-blocking CSI gRPC server, registers CSI-Addons services, detects runtime librbd/kernel features, and optionally starts profiling and node healing.

## Important APIs, Types, And Functions
`rbdDriver` stores the common CSI driver and RBD identity/node/controller servers plus a CSI-Addons server. `NewDriver`, `NewIdentityServer`, `NewControllerServer`, and `NewNodeServer` allocate runtime components. `Run(conf)` is the main entrypoint. `setupCSIAddonsServer` registers CSI-Addons identity, fencing, reclaim-space, replication, volume-group, and encryption-key-rotation services according to controller/node roles. `startProfiling` starts metrics and pprof handlers when enabled.

## Control Flow
`Run` first copies config values into RBD package globals and initializes journals. It builds the common CSI driver, adds controller and volume capability modes when in controller mode, conditionally advertises group snapshot support after `features.SupportsGroupSnapGetInfo`, fetches Kubernetes node labels/topology when needed, creates server structs, detects krbd and rbd-nbd features on node processes, configures CSI-Addons, starts the CSI gRPC server with identity/controller/node/group/SMS services, starts profiling, optionally launches the volume healer goroutine, and waits for server shutdown.

## State And Persistence
The file mutates package-level global RBD configuration (`rbdHardMaxCloneDepth`, snapshot limits, `skipForceFlatten`, `krbdFeatures`) and global journal configs. It creates long-lived gRPC server sockets/endpoints and a CSI-Addons endpoint. Node-label/topology data is read from Kubernetes but not persisted here.

## Dependencies And Integration Points
Integrates `internal/csi-common`, `internal/driver`, `internal/rbd`, `internal/rbd/features`, CSI-Addons RBD services, Kubernetes helpers, util config, logging, and kernel/librbd feature detection. It is the process-level connection point between CLI/config startup and all lower RBD controllers.

## Risks And Test Signals
Risks include global settings making per-cluster variation difficult, feature detection failures changing advertised capabilities, fatal startup on Kubernetes/topology or krbd parsing errors, and lifecycle interactions between the main server and CSI-Addons server. `driver_test.go` only smoke-tests CSI-Addons socket startup; broader startup and capability behavior needs integration testing.
