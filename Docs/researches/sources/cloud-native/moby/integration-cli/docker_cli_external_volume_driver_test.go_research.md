# sources/cloud-native/moby/integration-cli/docker_cli_external_volume_driver_test.go

Purpose: integration tests for legacy external volume driver plugins using a local HTTP test server and `/etc/docker/plugins/*.spec` registration. The suite validates driver activation, create/list/get/remove/path/mount/unmount/capability calls, daemon restart behavior, conflict handling, retries, and cleanup on copy or mount failure.

Important APIs/types/functions: `volumePluginName`, `eventCounter`, `DockerExternalVolumeSuite`, `volumePlugin`, `vol`, `newVolumePlugin`, `hostVolumePath`, and tests including `TestExternalVolumeDriverNamed`, `TestExternalVolumeDriverUnnamed`, `TestExternalVolumeDriverVolumesFrom`, `TestExternalVolumeDriverDeleteContainer`, `TestExternalVolumeDriverLookupNotBlocked`, `TestExternalVolumeDriverRetryNotImmediatelyExists`, `TestExternalVolumeDriverList`, `TestExternalVolumeDriverGet`, `TestExternalVolumeDriverWithDaemonRestart`, `TestExternalVolumeDriverCapabilities`, `TestExternalVolumeDriverOutOfBandDelete`, `TestExternalVolumeDriverUnmountOnMountFail`, and `TestExternalVolumeDriverUnmountOnCp`.

Control flow: `newVolumePlugin` installs HTTP handlers for Docker volume plugin endpoints and writes a spec file pointing to the server. Tests start daemons, run containers with `--volume-driver`, inspect mount metadata, compare endpoint counters, simulate down drivers and delayed driver registration, and mutate plugin-side volume maps to mimic out-of-band deletion.

State and persistence: creates `/etc/docker/plugins` specs, host volume paths under `/var/lib/docker/volumes`, plugin in-memory volume maps, Docker volumes, containers, and daemon root state. Some tests restart the daemon and expect plugin-backed volume metadata to persist.

Dependencies and integration points: local daemon, daemon harness, Docker volume CLI/API behavior, plugin protocol MIME type, HTTP test server, busybox, `container.MountPoint`, `volumetypes.Volume`, and volume scope constants.

Risks: writes to `/etc/docker/plugins` and `/var/lib/docker/volumes` require privileged local test environments. Endpoint counters are sensitive to internal caching behavior. Down-driver and retry tests rely on timing and network connection behavior.

Test signals: failures expose regressions in external plugin discovery, serialized volume driver calls, duplicate name conflict handling, plugin response validation, daemon restart restoration, scope caching, unmount semantics, or copy-triggered mount/unmount balancing.
