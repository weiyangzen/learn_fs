# sources/control-plane/rook/pkg/operator/k8sutil/cmdreporter/cmdreporter.go

Purpose: builds and runs Kubernetes Jobs that execute Rook's `cmd-reporter` utility and return stdout/stderr/retcode through a ConfigMap.

Important APIs/types/functions: constants `CmdReporterContainerName`, `CopyBinariesInitContainerName`, `CopyBinariesMountDir`; `CmdReporterInterface`; `CmdReporter`; `cmdReporterCfg`; `New`; `Job`; `Run`; `newWatcher`; `waitForConfigMap`; `initJobSpec`; `initContainers`; `container`; `needToCopyBinaries`; `copyBinariesVolAndMount`; `newInt32`; and `MockCmdReporterJob`.

Control flow: `New` validates required inputs, builds a job spec, and returns a reporter. Job spec creation optionally adds an init container to copy the rook binary when the run image differs from the rook image, builds the cmd-reporter container args using `util.CommandToCmdReporterFlagArgument`, adds host network, default service account, labels, rook version label, owner reference, and shared EmptyDir. `Run` deletes any stale result ConfigMap, runs a replaceable job, watches for the result ConfigMap with timeout and watcher restart on channel close, reads stdout/stderr/retcode keys, deletes the job and result ConfigMap best-effort, and returns command output even for nonzero retcode.

State and persistence: creates/deletes Kubernetes Jobs and result ConfigMaps. Uses ConfigMap presence as completion signal and ConfigMap data as output persistence.

Dependencies/integration: depends on client-go, k8sutil delete/job/version/owner helpers, Ceph resource defaults, and daemon util command encoding and ConfigMap key names.

Risks: any ConfigMap event on the watched name is treated as completion without validating data until later. Cleanup failures are logged but not returned. `Run` requires stale ConfigMap deletion to complete first, which can block on deletion behavior. No direct tests are in this subset; behavior depends on integration tests elsewhere.

Test signals: not directly tested here. The `MockCmdReporterJob` helper indicates other packages can test generated job specs without input validation.
