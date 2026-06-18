# sources/control-plane/rook/pkg/daemon/ceph/client/upgrade.go

This file provides upgrade safety helpers for Ceph daemon versions and ok-to-stop/ok-to-continue checks.

Version APIs include `GetCephMonVersion()` over `ceph version`, `GetAllCephDaemonVersions()` over `ceph versions`, and `LeastUptodateDaemonVersion()` which selects the lowest parsed version for a daemon type. `EnableReleaseOSDFunctionality()` runs `ceph osd require-osd-release`. `OkToStop()` handles special mon and OSD small-cluster bypasses, then retries `okToStopDaemon()` with daemon-specific retry config. `OkToContinue()` currently adds MDS-specific post-checks through `okToContinueMDSDaemon()`, which waits for active or standby-replay/standby MDS state.

OSD bypass helpers use `OsdListNum()`, `HostTree()`, and `buildHostListFromTree()` to skip ok-to-stop in fewer-than-three-OSD clusters, all-in-one host layouts, or missing-host CRUSH maps. `daemonMapEntry()` maps Ceph version JSON fields to daemon-type strings. State is read from Ceph version, OSD list, OSD tree, and status; no Kubernetes state is written.

Risks include conservative bypasses that allow upgrades without Ceph ok-to-stop, version selection over unordered maps, and dependency on CRUSH tree shape. `upgrade_test.go` covers command construction, retry config, daemon-map lookup, host filtering, OSD check decisions, and deterministic least-version selection.
