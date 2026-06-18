# sources/control-plane/rook/tests/integration/ceph_multi_cluster_test.go

Integration suite validating a core Rook Ceph cluster plus an external cluster connected to it. It checks health from both toolbox contexts.

`MultiClusterDeploySuite` stores core/external settings, manifests, installer, toolbox command names, and a pool name. Setup configures a core cluster in `multi-core`, an external cluster in `multi-external`, runs `tests/scripts/localPathPV.sh` on the scratch device, starts the core cluster, creates a test pool, then calls `CreateRookExternalCluster`. The test switches global `client.RunAllCephCommandsInToolboxPod` between core and external toolbox commands and validates install/health.

State includes local-path PV host setup, core Rook cluster resources, external cluster resources, a Ceph pool, and a mutated global toolbox command function. Dependencies are local path PV script, `CephInstaller` external-cluster support, Rook clients, shared deploy checks, and Ceph toolbox dispatch.

Risks: global toolbox function mutation is unsafe for parallel suites; local PV script depends on host scratch device; pool deletion failure is logged but not fatal; external setup diagnostics are namespace-limited. Signals include local PV command success, core install pod counts, core health, external health, pool lifecycle, and multi-namespace uninstall.
