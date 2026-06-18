<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/beegfs-csi-driver/main.go -->
# sources/control-plane/beegfs-csi-driver/cmd/beegfs-csi-driver/main.go

## Purpose
This is the executable entry point for the BeeGFS CSI driver process. It parses command-line flags, prints version information when requested, constructs the driver, and starts it.

## Important APIs, Types, and Functions
Flags configure connection auth path, TLS cert path, plugin config path, controller-service data directory, CSI driver name, CSI endpoint, node ID, version output, client config template path, and node-unstage timeout. `main()` initializes klog, sets `logtostderr`, parses flags, handles `--version`, and delegates to `handle()`. `handle()` calls `beegfs.NewBeegfsDriver()` and then `driver.Run()`.

## Control Flow
Startup is linear. Failure to set klog flags or initialize the driver exits through `beegfs.LogFatal()`. Successful initialization blocks in `driver.Run()`. Version mode prints the executable basename and build-provided version string, then returns without starting the driver.

## State and Persistence
The file itself persists no state. It passes `cs-data-dir` to the driver, which is used by controller service logic for client configuration and mounts. The build process injects `version`.

## Dependencies and Integration Points
It depends on `github.com/netapp/beegfs-csi-driver/pkg/beegfs`, standard flags, and klog. Kubernetes manifests pass these flags to controller and node containers, and the Makefile injects linker flags through release-tools.

## Risks
Default endpoint is `unix://tmp/csi.sock`, while deployment manifests override it with `/csi/csi.sock`; local runs must set an appropriate endpoint. Empty `node-id` may be invalid for node service behavior depending on driver internals. Fatal logging makes startup errors process-terminating.

## Test Signals
Signals include `--version`, flag parsing, `NewBeegfsDriver()` construction tests in package code, deployment smoke tests that verify the CSI socket is created, and Kubernetes sidecar connectivity.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/beegfs-csi-driver/main.go -->
