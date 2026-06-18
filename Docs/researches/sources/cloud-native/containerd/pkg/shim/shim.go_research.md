<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim.go -->
# sources/cloud-native/containerd/pkg/shim/shim.go

## Purpose
Main shim binary bootstrap and server runner for the v2/v3 shim lifecycle.

## Important APIs, Types, And Functions
Defines Publisher, StopStatus, Shim, Opts, Config, TTRPC service/interceptor interfaces, parseFlags, setRuntime, setLogger, RunShim, runInfo, run, serve, dumpStacks, and setupPprof.

## Control Flow
run parses flags, handles version/info/delete/start actions, builds namespace and shutdown contexts, falls back from new bootstrap proto to deprecated fields, starts managers, registers plugins, builds ttrpc server/interceptors, serves until signal/reaper shutdown, and cleans sockets.

## State And Persistence
Process-global flags are parsed into package vars. Runtime tuning changes GOGC and optionally GOMAXPROCS. Plugins get state dirs under bundle path. Socket-dir symlink/address files support cleanup.

## Dependencies And Integration Points
Integrates boot/task APIs, plugin registry, namespaces, shutdown service, protobuf helpers, event publisher, ttrpc server, platform socket/signal helpers, and optional pprof plugin.

## Risks And Edge Cases
Complex lifecycle risks include partial bootstrap reads, logger FIFO setup failure, missing ttrpc services, plugin init failures, signal/reaper races, socket leaks after crashes, and Windows named-pipe readiness timing.

## Test Signals
shim_test.go checks runtime GOMAXPROCS and context options; other shim util tests cover sockets/interceptors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim.go -->
