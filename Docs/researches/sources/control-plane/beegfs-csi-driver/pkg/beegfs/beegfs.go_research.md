<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs.go

## Purpose
Core BeeGFS CSI driver initialization and internal volume model.

## Important APIs, Types, And Functions
Defines `beegfs`, `beegfsVolume`, `stripePatternConfig`, `permissionsConfig`, and `reqParameters`. Exports `NewBeegfsDriver` and `NewBeegfsDriverSanity`. Key helpers are `newBeegfsDriver`, `Run`, `newBeegfsVolume`, `newBeegfsVolumeFromID`, `getDefaultClientConfTemplatePath`, and permission mode methods.

## Control Flow
Driver creation verifies required strings, verifies the BeeGFS client module for real driver mode, reads client config template, parses plugin config/connAuth/TLS files, creates controller service data dir, initializes identity/node/controller servers, and later runs a non-blocking gRPC server.

## State And Persistence
Persists controller service data directory on disk with 0750 permissions. `beegfsVolume` computes host and BeeGFS-root paths for mount dirs, client config, connAuth/TLS files, CSI metadata, and volume directories.

## Dependencies And Integration Points
Depends on operator API config types, config parsing helpers, filesystem abstraction `fs/fsutil`, identity/node/controller server constructors, and BeeGFS URL parsing helpers.

## Risks And Edge Cases
Default client config discovery depends on host/container path assumptions. `vendorVersion` is package-global and mutable during initialization. Special Unix permission bits require custom conversion because Go `os.FileMode` encodes them differently.

## Test Signals
Unit tests cover initialization failure cases, permission helpers, volume path construction, URL-derived volume construction, and default client config path discovery with afero.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs.go -->
