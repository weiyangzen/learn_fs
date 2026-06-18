# sources/control-plane/rook/tests/integration/ceph_mgr_test.go

Ceph manager Rook orchestrator integration suite. It validates `ceph orch device ls`, `status`, `host ls`, and `ls` against Kubernetes state.

`CephMgrSuite` installs a `mgr-ns` cluster with OSD creation skipped, waits for the Rook orchestrator backend, and configures a no-provisioner `local-storage` StorageClass in mgr config. JSON structs `host`, `serviceStatus`, and `service` model Ceph command output. `executeWithRetry`, `enableOrchestratorModule`, and `waitForOrchestrationModule` wrap Ceph CLI behavior. Tests compare orchestrator hosts with Kubernetes node hostnames and service running counts with pods selected by labels.

State includes a Ceph cluster, `local-storage` StorageClass, Ceph mgr config `mgr/rook/storage_class`, and possibly enabled Rook mgr module/backend. Dependencies are Ceph CLI through installer/toolbox, Rook orchestrator module, `k8sutil`, Kubernetes node/pod APIs, JSON output formats, and testify.

Risks: non-`*exec.ExitError` command failures can panic in `waitForOrchestrationModule`; exact status text is brittle; service label derivation assumes fixed Rook labels; mgr config changes are cluster-level. Signals include successful orch commands, JSON parse success, backend `rook`, host equality, service count equality, and storage-class config success.
