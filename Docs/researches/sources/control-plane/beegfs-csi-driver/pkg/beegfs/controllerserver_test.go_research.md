# sources/control-plane/beegfs-csi-driver/pkg/beegfs/controllerserver_test.go

Purpose: Tests controller helper behavior around CreateVolume parameter parsing and DeleteVolume node-tracking cleanup. It defines the behavioral contract for stripe pattern parameters, permission parameters, volume deletion waiting, and required parameter validation.

Important APIs/types/functions: `TestGetStripePatternConfigFromParams`, `TestGetPermissionsConfigFromParams`, `TestDeleteVolumeUntilWaitEmptyNodesDir`, `TestDeleteVolumeUntilWaitNoCSIDir`, `TestDeleteVolumeUntilWaitNodesDirNeverEmpties`, `TestDeleteVolumeUntilWaitNodesDirEmptiesEventually`, and `TestValidateReqParams`.

Control flow: Stripe tests pass maps with valid and invalid `stripePattern/...` keys and assert parsed config or errors. Permission tests parse UID/GID as 32-bit decimal values and mode as octal up to 12 bits. Delete tests set up an in-memory BeeGFS-like directory tree, optionally create node-tracking files, then call `deleteVolumeUntilWait` with zero or nonzero waits. One test removes a node tracking file asynchronously after two seconds to verify polling exits before timeout. Request parameter tests ensure `sysMgmtdHost` and `volDirBasePath` are required/normalized and unknown keys are rejected.

State and persistence: Uses `afero.NewMemMapFs` to build and remove directory trees in memory. Parameter parser tests mutate input maps because the production functions delete recognized keys; each table entry supplies fresh maps.

Dependencies and integration points: Depends on config constants and structs from other BeeGFS package files, `newBeegfsVolume`, and `afero`. It directly supports the controller's CSI Create/Delete request paths.

Risks: Some invalid stripe test cases use lowercase parameter keys, so they simultaneously exercise unknown-key and bad-value behavior. Deletion wait tests depend on real sleeps and wall-clock timing, which can be slow or flaky under heavy load. The tests focus helper functions rather than full `CreateVolume`/`DeleteVolume` CSI method behavior.

Test signals: Strong validation for boundary values: too-large UID/GID, non-octal modes, extra leading zeroes, empty base path normalized to `/`, extra unknown params rejected, and delete cleanup removing both `.csi` and volume directories under multiple node-tracking states.
