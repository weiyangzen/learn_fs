# sources/control-plane/juicefs-csi-driver/pkg/controller/mountinfo_test.go

Purpose: Ginkgo spec for mountinfo target resolution and status classification.

Important tests: synthetic mount rows verify normal base and subPath resolution, duplicate count aggregation, invalid target rejection, stat errors as unexpected, absent mountinfo as not-mounted, ENOTCONN as corrupt, not-exist as missing, and inconsistent roots.

Control flow/state: `mockMountInfoTable` creates fake `k8sMount.MountInfo` rows. `os.Stat` is monkey-patched with ordered return values. Specs run through `controller_suite_test.go`.

Dependencies/integration: Ginkgo/Gomega, gomonkey, Kubernetes mount structs, `os`, and syscall errors. It directly protects `mountinfo.go` behavior used by `PodDriver.recover`.

Risks/gaps: does not use real `/proc/self/mountinfo`, does not exercise timeout behavior, and does not independently table-test `getPodUid`/`getPVName`.

Test signal: strong for synthetic classification; limited for live node behavior.
