<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/util_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/util_test.go

### Purpose
`util_test.go` is the main unit-test specification for the broad helpers in `util.go`. It covers parsing, version gates, mount-command introspection, string helpers, time-zone behavior, map/slice utilities, and input cleanup.

### Important APIs, Types, And Functions
The file tests `ContainsString`, `ParseEndpoint`, `GetReferenceKey`, `GetTimeAfterDelay`, `GetTime`, `QuoteForShell`, `StripPasswd`, `CheckDynamicPV`, `ContainsPrefix`, `StripReadonlyOption`, `CheckExpectValue`, `ImageResol`, `ParseToBytes`, `parseClientVersionFromImage`, `SupportFusePass`, `GetMountPathOfPod`, `parseMntPath`, `SupportUpgradeRecreate`, `SupportUpgradeBinary`, `GetMountOptionsOfPod`, `SortBy`, `MergeMap`, `DeDuplicate`, `GetMountPathOfSidecar`, `SupportQuotaPathCreate`, `IsConfigEncrypted`, and `RemoveIllegalChars`.

### Control Flow
Most tests are table driven. Some use gomonkey/goconvey to force `url.Parse`, `os.Remove`, and `os.IsNotExist` error paths. Time tests explicitly alter `time.Local` to prove RFC3339 output round-trips correctly across UTC, UTC+8, and UTC-5 while legacy zone-less strings are parsed in local time. Mount path tests feed CE/EE command strings with init config, ACL symlink setup, `exec`, subpath creation, and malformed mount destinations.

### State, Persistence, And Dependencies
The tests are mostly pure and in-memory. `ParseEndpoint` can remove a unix socket path, but error tests monkey patch filesystem calls. Dependencies include gomonkey, goconvey, Kubernetes corev1 structs, metav1, common constants, and local time-zone manipulation.

### Integration Points
This suite protects behavior used by CSI server startup, mount pod lifecycle, controller cleanup, webhook sidecar handling, feature-gate decisions, and dashboard diagnostics. The time-zone tests specifically preserve compatibility between new RFC3339 scheduled times and legacy local-time timestamps.

### Risks
The tests do not cover proc mountinfo parsing, actual unmount execution, disk usage errors, Prometheus registry labels, snapshot handle helpers, or generic pointer/copy helpers. Some tests depend on exact current time to the second and allow small drift only in the explicit round-trip test. The tested command parsing still assumes the mount command is the final shell line.

### Test Signals
Strong signals include unsupported endpoint rejection, unix socket remove error handling, SHA reference-key stability, local-vs-UTC time parsing, password redaction, dynamic PV regex, CE/EE image classification, byte units, fuse-pass and upgrade thresholds, mount path extraction from several command layouts, map merge precedence, duplicate removal preserving order, sidecar label/container validation, quota support thresholds, config encryption booleans, and ASCII/nonprintable cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/util_test.go -->
