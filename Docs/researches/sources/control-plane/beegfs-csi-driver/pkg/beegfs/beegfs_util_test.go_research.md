# sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_util_test.go

Purpose: Unit-tests the shared BeeGFS utility layer, especially URL formatting, client configuration rendering, BeeGFS 7/8 config compatibility, filesystem-specific config squashing, ephemeral port selection, mount option handling, and CSI capability validation.

Important APIs/types/functions: Defines `TestWriteClientFilesTemplate`, expected rendered config constants for BeeGFS 7 and 8 templates, and table-driven tests for `NewBeegfsURL`, `parseBeegfsURL`, `writeClientFiles`, `squashConfigForSysMgmtdHost`, `getEphemeralPortUDP`, `sanitizeVolumeID`, `isValidVolumeCapabilities`, `addContextToMountOptionsIfNecessary`, and `removeInvalidMountOptions`.

Control flow: Tests swap package-level `fs` and `fsutil` to `afero.NewMemMapFs` for client file rendering, create template/config directories, build `beegfsVolume` instances, call helpers, and read back generated files. The variable UDP client port is masked with a regex before comparing generated INI content. BeeGFS 8 tests verify `connClientPort` and `connMgmtdPort` handling, including failure when deprecated TCP/UDP management ports disagree.

State and persistence: Test state is isolated mostly in memory via `afero`, except `getEphemeralPortUDP` uses a real UDP socket. Tests mutate global filesystem variables and rely on later tests setting their own backing filesystem where needed.

Dependencies and integration points: Uses BeeGFS operator API config structs, CSI protobuf volume capability structs, package helpers from `beegfs_util.go`, and `afero`. The tests verify compatibility expectations that controller and node service operations depend on before mounting or calling `beegfs-ctl`.

Risks: The expected INI output is formatting-sensitive, so changes in `go-ini` rendering could break tests even if semantics are unchanged. Global filesystem mutation can leak between tests if a new test forgets to reset it. Capability validation tests are narrow: they assert block is rejected and mount is accepted but do not deeply examine all access modes because the driver accepts all CSI access modes for mounted volumes.

Test signals: Strong coverage for client file rendering and compatibility paths. The tests explicitly guard secret/auth file contents, networking filter files, RDMA interface files, hash fallback for long IDs, duplicate/cfgFile mount option removal, and default SELinux context insertion.
