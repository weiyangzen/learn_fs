# sources/cloud-native/containerd/core/metrics/cgroups/metrics_test.go

Purpose: regression test for a collector deadlock reported in containerd issue 6772, where metric collection and task addition could contend on locks.

Important APIs and types: `TestRegressionIssue6772`, local `Collector` interface, and `mockStatT` implementing `common.Statable`.

Control flow: the test creates a metrics namespace and chooses v1 or v2 collector based on host cgroup mode. One goroutine continuously calls namespace `Collect`, while many goroutines concurrently call collector `Add` with const labels. A metric drain goroutine prevents channel backpressure. The test fails if any add errors or if adds do not finish within 30 seconds.

State and persistence: no persistent state. Runtime state is collector task maps, namespace labels, and metrics channels.

Dependencies and integration: uses cgroups mode detection, v1/v2 collectors, typeurl marshaling of empty v1/v2 metrics payloads, Docker metrics namespace, and Prometheus metric channels.

Risks: this is a timing/concurrency regression test and may be sensitive to heavily loaded CI, though the timeout is generous. It validates absence of a deadlock but not emitted metric values.

Test signals: strong concurrency signal for `Collector.Add` versus `Namespace.Collect` lock ordering.
